import os
os.environ['QT_QPA_PLATFORM']='offscreen'
import unittest
from unittest.mock import patch
from PyQt6.QtWidgets import QApplication
from dotctl import core, gui

class GuiTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app=QApplication.instance() or QApplication([])

    def test_search_finds_up_to_date_module_from_other_category(self):
        with patch.object(gui.MainWindow,'refresh'),patch.object(core,'load_state',return_value={}):
            window=gui.MainWindow()
            window.mods={'app-blender':core.Module('app-blender','Blender Launcher','creative'),
                         'foo':core.Module('foo','Foo','apps')}
            window.st={'app-blender':core.OK,'foo':core.ABSENT}
            window.prof={'modules':['foo']}
            window.set_mode(gui.UPDATES)
            self.assertNotIn('app-blender',window.cards)
            window.search.setText('blender')
            self.assertEqual(list(window.cards),['app-blender'])
            window.cards['app-blender'].cb.setChecked(True)
            window.search.clear()
            self.assertIn('app-blender',window.selection())
            window.set_mode(gui.NEW)
            self.assertIn('app-blender',window.cards)
            self.assertFalse(window.cards['app-blender'].cb.isChecked())
            window.close()

    def test_subparts_from_parent_are_not_silently_preselected(self):
        parent=core.Module('parent','Parent','apps')
        child=core.Module('parent/a','A','apps',parent='parent')
        parent.parts=[child]
        state={'parent':{'requested':True},'parent/a':{'requested':False}}
        with patch.object(gui.MainWindow,'refresh'),patch.object(core,'load_state',return_value=state):
            window=gui.MainWindow()
            window.mods={'parent':parent,'parent/a':child}
            window.st={'parent':core.UPDATE,'parent/a':core.UPDATE}
            window.prof={'modules':['parent']}
            window.mode=gui.UPDATES
            window.reset_checks()
            self.assertTrue(window.checked['parent'])
            self.assertFalse(window.checked['parent/a'])
            self.assertNotIn('parent/a',window.visible_ids())
            window.search.setText('parent/a')
            self.assertIn('parent/a',window.cards)
            self.assertFalse(window.cards['parent/a'].cb.isChecked())
            window.close()
