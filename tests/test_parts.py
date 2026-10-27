import contextlib
import io
import json
import os
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch

from dotctl import core, options, cli

class PartsTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.private = self.root/'private'; self.private.mkdir()
        self.patch = contextlib.ExitStack(); self.addCleanup(self.patch.close)
        self.patch.enter_context(patch.object(options,'path',return_value=self.private/'settings/test.json'))
        self.patch.enter_context(patch.object(Path,'home',return_value=self.root))
        self.patch.enter_context(patch.object(core,'STATE_FILE',self.root/'state.json'))
        self.patch.enter_context(patch.object(core,'context_env',return_value={'HOME':str(self.root)}))
        self.patch.enter_context(patch.object(core,'missing_packages',return_value=[]))
        self.patch.enter_context(patch.object(core,'plan_commands',return_value=[]))
        folder=self.root/'modules/demo'; folder.mkdir(parents=True)
        (folder/'a.txt').write_text('A')
        (folder/'b.txt').write_text('B')
        self.parent=core.Module('demo','Demo','apps',path=folder)
        self.a=core.Module('demo/a','A','apps',path=folder,parent='demo',
                           files=[core.FileSpec('a.txt',str(self.root/'installed/a.txt'))])
        self.b=core.Module('demo/b','B','apps',path=folder,parent='demo',
                           files=[core.FileSpec('b.txt',str(self.root/'installed/b.txt'))])
        self.parent.parts=[self.a,self.b]
        self.mods={m.id:m for m in [self.parent,self.a,self.b]}
        self.patch.enter_context(patch.object(core,'load_modules',return_value=self.mods))

    def test_explicit_part_applies_only_it_and_shared_base(self):
        self.assertEqual([m.id for m in core.resolve(['demo/a'],self.mods)],['demo','demo/a'])
        self.assertEqual(core.apply(['demo/a'],log=lambda *_:None),0)
        self.assertTrue((self.root/'installed/a.txt').exists())
        self.assertFalse((self.root/'installed/b.txt').exists())
        self.assertNotIn('demo/b',core.load_state())

    def test_saved_selection_controls_parent_and_empty_means_base_only(self):
        options.save(self.parent,{},['demo/b'])
        self.assertEqual([m.id for m in core.resolve(['demo'],self.mods)],['demo','demo/b'])
        self.assertEqual(core.apply(['demo'],log=lambda *_:None),0)
        self.assertFalse((self.root/'installed/a.txt').exists())
        options.save(self.parent,{},[])
        self.assertEqual([m.id for m in core.resolve(['demo'],self.mods)],['demo'])
        self.assertTrue((self.root/'installed/b.txt').exists())

    def test_preview_does_not_save_and_excludes_other_parts(self):
        with patch.object(core,'DOTFILES',self.root):
            plan=core.application_plan(['demo'],{'demo':['demo/a']})
        self.assertEqual([m['id'] for m in plan['modules']],['demo','demo/a'])
        self.assertFalse(options.path().exists())
        self.assertFalse((self.root/'installed').exists())

    def test_other_part_changes_do_not_invalidate_selected_part(self):
        a_hash=self.a.content_hash(); base_hash=self.parent.content_hash()
        (self.parent.path/'b.txt').write_text('changed B')
        self.assertEqual(self.a.content_hash(),a_hash)
        self.assertEqual(self.parent.content_hash(),base_hash)

    def test_cycles_fail_before_execution(self):
        self.a.requires=['demo/b'];self.b.requires=['demo/a']
        with self.assertRaisesRegex(ValueError,'circulaire'):core.resolve(['demo/a'],self.mods)

    def test_typed_values_are_private_and_secrets_not_in_plan(self):
        self.a.inputs=[options.Input('ENABLED',type='bool',default=True),
                       options.Input('TOKEN',type='secret',required=True)]
        options.save(self.parent,{'ENABLED':False,'TOKEN':'not-public'},['demo/a'])
        self.assertEqual(options.environment()['ENABLED'],'false')
        self.assertEqual(os.stat(options.path()).st_mode & 0o777,0o600)
        with patch.object(core,'DOTFILES',self.root):
            text=json.dumps(core.application_plan(['demo/a']))
        self.assertNotIn('not-public',text)
        self.assertTrue(options.load()['secrets']['TOKEN'])

    def test_unknown_parts_and_bad_fields_leave_settings_unchanged(self):
        options.save(self.parent,{},['demo/a']);before=options.path().read_bytes()
        for values,parts in [({},['demo/nope']),({'BOGUS':'value'},['demo/a'])]:
            with self.assertRaises(ValueError):options.save(self.parent,values,parts)
            self.assertEqual(options.path().read_bytes(),before)

    def test_cli_configure_selects_part_and_does_not_apply(self):
        with contextlib.redirect_stdout(io.StringIO()):
            cli.cmd_configure(['demo','--parts','b'])
        self.assertEqual(options.selected(self.parent),['demo/b'])
        self.assertFalse((self.root/'installed').exists())

    def test_failed_base_blocks_child(self):
        (self.parent.path/'apply.sh').write_text('exit 1\n')
        self.assertGreater(core.apply(['demo/a'],log=lambda *_:None),0)
        self.assertFalse((self.root/'installed/a.txt').exists())

    def test_missing_required_field_blocks_dependent_part(self):
        self.parent.inputs=[options.Input('NEEDED',required=True)]
        self.assertGreater(core.apply(['demo/a'],log=lambda *_:None),0)
        self.assertFalse((self.root/'installed/a.txt').exists())

    def test_false_boolean_is_valid_and_path_must_exist(self):
        self.assertFalse(options.Input('FLAG',type='bool',required=True).normalize(False))
        with self.assertRaises(ValueError):options.Input('DIR',type='path',must_exist=True).normalize('/not-a-real-dir-xx')
        with self.assertRaises(ValueError):options.Input('FLAG',type='bool').normalize('yes')

    def test_partial_capture_ignores_sibling(self):
        (self.root/'installed').mkdir()
        (self.root/'installed/a.txt').write_text('new A')
        (self.root/'installed/b.txt').write_text('new B')
        core.capture('demo/a',log=lambda *_:None)
        self.assertEqual((self.parent.path/'a.txt').read_text(),'new A')
        self.assertEqual((self.parent.path/'b.txt').read_text(),'B')

    def test_child_template_receives_shared_default(self):
        self.parent.inputs=[options.Input('SHARED_VALUE',default='common')]
        (self.parent.path/'a.txt').write_text('${SHARED_VALUE}')
        self.a.files[0].template=True
        self.assertEqual(core.apply(['demo/a'],log=lambda *_:None),0)
        self.assertEqual((self.root/'installed/a.txt').read_text(),'common')
