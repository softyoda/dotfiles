import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import tempfile
from pathlib import Path
import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from dotctl import core, options
from dotctl.module_gui import ModuleDialog, agent_reference

class ModuleDialogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls): cls.app=QApplication.instance() or QApplication([])

    def test_unselected_part_fields_are_not_saved_or_required(self):
        root=core.Module('demo','Demo','apps')
        part=core.Module('demo/extra','Extra','apps',parent='demo',inputs=[options.Input('MISSING',required=True)])
        root.parts=[part]
        with patch.object(core,'context_env',return_value={}),patch.object(options,'selected',return_value=[]), \
             patch.object(core,'load_modules',return_value={'demo':root,'demo/extra':part}):
            dialog=ModuleDialog(root)
            parts,values,changed=dialog.collect()
            self.assertEqual(parts,[])
            self.assertEqual(values,{})
            dialog.part_checks[part.id].setChecked(True)
            with self.assertRaises(ValueError):dialog.collect()
            dialog.editors[(part.id,'MISSING')][1].setText('chosen')
            self.assertEqual(dialog.collect()[2],{'MISSING':'chosen'})
            dialog.close()

    def test_boolean_and_path_widgets_have_same_semantics_as_cli(self):
        module=core.Module('demo','Demo','apps',inputs=[options.Input('FLAG',type='bool',default=True),
                          options.Input('DIRECTORY',type='path')])
        with patch.object(core,'context_env',return_value={}):
            dialog=ModuleDialog(module)
            self.assertTrue(dialog.collect()[1]['FLAG'])
            dialog.editors[('demo','FLAG')][1].setChecked(False)
            dialog.editors[('demo','DIRECTORY')][1].setText('/tmp/example')
            self.assertEqual(dialog.collect()[2],{'FLAG':False,'DIRECTORY':'/tmp/example'})
            dialog.close()

    def test_agent_reference_contains_stable_id_not_secret(self):
        m=core.Module('demo/extra','Extra','apps',parent='demo',path=Path('/any/modules/demo'))
        text=agent_reference(m)
        self.assertIn('dotctl apply demo/extra',text)
        self.assertIn('modules/demo/module.toml',text)
        self.assertIn('settings/<hostname>.json',text)
