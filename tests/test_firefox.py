import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch
import zipfile
from dotctl import core, firefox as ff

class FirefoxTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.source = self.root / 'source'
        self.source.mkdir()
        self.private = self.root / 'private'
        self.private.mkdir()
        self.patcher = patch.object(core, 'private_dir', return_value=self.private)
        self.patcher.start()
        self.addCleanup(self.patcher.stop)
        self.uid = '12345678-1234-1234-1234-123456789abc'
        self.origin = 'moz-extension+++' + self.uid
        self.eid = ff.EXTENSIONS['ublock']
        ff._merge_prefs(self.source/'prefs.js', {
            'toolkit.tabbox.switchByScrolling': True,
            'browser.tabs.warnOnClose': False,
            'identity.fxaccounts.account.device.name': 'private',
            'extensions.webextensions.uuids': json.dumps({self.eid:self.uid})})
        ext = self.source / 'extensions'
        ext.mkdir()
        with zipfile.ZipFile(ext / (self.eid+'.xpi'), 'w') as z:
            z.writestr('manifest.json', json.dumps({'browser_specific_settings': {'gecko': {'id':self.eid}}}))
        data = self.source/'storage/default'/self.origin
        data.mkdir(parents=True)
        (data/'filters').write_text('user filter')

    def test_roundtrip_selected_prefs_and_extension_preserves_unrelated_data(self):
        snapshot = ff.capture(self.source, 'release', ['prefs','ublock'])
        self.assertNotIn('identity.fxaccounts.account.device.name', (snapshot/'prefs.json').read_text())
        target = self.root/'target'
        target.mkdir()
        ff._merge_prefs(target/'prefs.js', {'browser.tabs.warnOnClose': True, 'unrelated.setting':42,
            'extensions.webextensions.uuids': json.dumps({'other@ext':'87654321-1234-1234-1234-123456789abc'})})
        backup = ff.restore(snapshot, target, ['prefs','ublock'], ['toolkit.tabbox.switchByScrolling'])
        prefs = ff.preferences(target/'prefs.js')
        self.assertTrue(prefs['toolkit.tabbox.switchByScrolling'])
        self.assertTrue(prefs['browser.tabs.warnOnClose'])
        self.assertEqual(prefs['unrelated.setting'],42)
        self.assertIn('other@ext',json.loads(prefs['extensions.webextensions.uuids']))
        self.assertNotIn('extensions.webextensions.uuids', ff.preferences(target/'user.js'))
        self.assertEqual((target/'storage/default'/self.origin/'filters').read_text(),'user filter')
        self.assertTrue((backup/'prefs.js').exists())
        ff.restore(snapshot, target, ['ublock'])
        self.assertEqual((target/'storage/default'/self.origin/'filters').read_text(),'user filter')

    def test_running_firefox_lock_prevents_capture(self):
        proc = subprocess.Popen([sys.executable,'-c',
            'import fcntl,sys; f=open(sys.argv[1],"w"); fcntl.lockf(f,fcntl.LOCK_EX); print("locked",flush=True); sys.stdin.read()',
            str(self.source/'.parentlock')],stdin=subprocess.PIPE,stdout=subprocess.PIPE,text=True)
        try:
            self.assertEqual(proc.stdout.readline().strip(),'locked')
            with self.assertRaisesRegex(RuntimeError,'Fermez Firefox'):
                ff.capture(self.source,'release',['prefs'])
        finally:
            proc.communicate('')
        self.assertFalse((self.private/'firefox').exists())

    def test_bad_origin_is_rejected_before_changes(self):
        snapshot = ff.capture(self.source,'release',['ublock'])
        p=snapshot/'manifest.json'
        data=json.loads(p.read_text())
        data['components']['ublock']['origins']=['../../outside']
        p.write_text(json.dumps(data))
        with self.assertRaisesRegex(RuntimeError,'Chemin'):
            ff.restore(snapshot,self.source,['ublock'])
        self.assertFalse((self.source/'dotfiles-backups').exists())

    def test_write_error_rolls_back(self):
        snapshot=ff.capture(self.source,'release',['prefs','ublock'])
        before=(self.source/'prefs.js').read_bytes()
        with patch.object(ff,'_merge_prefs',side_effect=OSError('disk full')):
            with self.assertRaises(OSError):ff.restore(snapshot,self.source,['prefs','ublock'])
        self.assertEqual((self.source/'prefs.js').read_bytes(),before)
        self.assertEqual((self.source/'storage/default'/self.origin/'filters').read_text(),'user filter')

    def test_unavailable_extension_does_not_publish_partial_snapshot(self):
        with self.assertRaisesRegex(RuntimeError,'absent'):
            ff.capture(self.source,'release',['prefs','userscripts'])
        self.assertEqual(ff.snapshots(),[])

    def test_explicit_extra_preference_is_transportable(self):
        ff._merge_prefs(self.source/'prefs.js', {'browser.example.custom': True})
        snap=ff.capture(self.source,'release',['prefs'],['browser.example.custom'])
        target=self.root/'target'; target.mkdir()
        ff.restore(snap,target,['prefs'])
        self.assertTrue(ff.preferences(target/'prefs.js')['browser.example.custom'])
