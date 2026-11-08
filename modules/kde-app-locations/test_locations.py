#!/usr/bin/env python3
import importlib.machinery,importlib.util,pathlib,tempfile,unittest
source=pathlib.Path(__file__).parent/'files/kde-app-locations';loader=importlib.machinery.SourceFileLoader('locations',str(source));spec=importlib.util.spec_from_loader(loader.name,loader);m=importlib.util.module_from_spec(spec);loader.exec_module(m)
BASE='[Desktop Entry]\nType=Application\nName=Example\nExec=/bin/true\nActions=Original;\n\n[Desktop Action Original]\nName=Existing action\nExec=/bin/true\n'
class Locations(unittest.TestCase):
 def setUp(self):
  self.tmp=tempfile.TemporaryDirectory();self.root=pathlib.Path(self.tmp.name);self.user=self.root/'user/applications';self.system=self.root/'system/applications';self.user.mkdir(parents=True);self.system.mkdir(parents=True);self.state=self.root/'state.json';self.helper=self.root/'helper with spaces';self.roots=[self.user,self.system]
 def tearDown(self):self.tmp.cleanup()
 def sync(self,**kw):return m.sync(self.roots,self.state,self.helper,**kw)
 def test_generated_updates_and_uninstall(self):
  p=self.system/'example.desktop';p.write_text(BASE);self.assertEqual(len(self.sync()),1);self.assertEqual(self.sync(),[])
  generated=self.user/p.name;self.assertIn('DotfilesOpenProgram',generated.read_text());self.assertEqual(p.read_text(),BASE)
  p.write_text(BASE.replace('Name=Example','Name=Updated'));self.sync();self.assertIn('Name=Updated',generated.read_text())
  p.unlink();self.sync();self.assertFalse(generated.exists())
 def test_personal_edits_and_original_actions_survive_restore(self):
  p=self.user/'example.desktop';p.write_text(BASE);self.sync();self.assertIn('Actions=Original;DotfilesOpenProgram;',p.read_text());p.write_text(p.read_text().replace('Name=Example','Name=My title'))
  self.sync();self.assertEqual(self.sync(),[]);self.sync(restore=True);self.assertEqual(p.read_text(),BASE.replace('Name=Example','Name=My title'))
 def test_generated_user_edit_is_preserved(self):
  p=self.system/'example.desktop';p.write_text(BASE);self.sync();q=self.user/p.name;q.write_text(q.read_text().replace('Name=Example','Name=Mine'));self.sync();p.unlink();self.sync();self.assertTrue(q.exists());self.sync(restore=True);self.assertIn('Name=Mine',q.read_text())
 def test_symlink_restored_without_touching_target(self):
  target=self.system/'example.desktop';target.write_text(BASE);p=self.user/'example.desktop';p.symlink_to(target);self.sync();self.assertFalse(p.is_symlink());self.assertEqual(target.read_text(),BASE);self.assertEqual(self.sync(),[]);self.sync(restore=True);self.assertTrue(p.is_symlink());self.assertEqual(p.resolve(),target)
 def test_hidden_updated_system_app_is_not_kept_visible(self):
  p=self.system/'example.desktop';p.write_text(BASE);self.sync();p.write_text(BASE+'\nHidden=true\n') # use main section below, not original action
  p.write_text(BASE.replace('Name=Example','Name=Example\nHidden=true'));self.sync();self.assertFalse((self.user/p.name).exists())
 def test_exec_parsing_never_executes_command(self):
  binary=self.root/'a program; not a shell';binary.write_text('fake');binary.chmod(0o755)
  text='[Desktop Entry]\nType=Application\nExec=env MODE=test "'+str(binary)+'" %f\n';self.assertEqual(m.resolve_executable(text),binary)
  marker=self.root/'must-not-exist';self.assertEqual(m.resolve_executable('[Desktop Entry]\nExec=/bin/sh -c "touch '+str(marker)+'"\n'),pathlib.Path('/bin/sh').resolve());self.assertFalse(marker.exists())
 def test_action_carries_explicit_launcher_uri(self):
  p=self.system/'with spaces.desktop';p.write_text(BASE);self.sync();text=(self.user/p.name).read_text();self.assertNotIn('%k',text);self.assertIn('with%%20spaces.desktop',text)
 def test_file_url_with_spaces(self):
  path=self.root/'with spaces.desktop';self.assertEqual(m.reference(path.as_uri()),path)
if __name__=='__main__':unittest.main()
