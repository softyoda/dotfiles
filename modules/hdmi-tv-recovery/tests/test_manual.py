import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest.mock import Mock

spec = importlib.util.spec_from_file_location('hdmi_manual', Path(__file__).parents[1]/'files/manual.py')
manual = importlib.util.module_from_spec(spec)
spec.loader.exec_module(manual)

class Recovery(unittest.TestCase):
    def output(self):
        return {'name':'HDMI-A-1', 'currentModeId':'1', 'modes':[
            {'id':'1','refreshRate':60,'size':{'width':3840,'height':2160}},
            {'id':'custom','refreshRate':5,'size':{'width':3840,'height':11000}},
            {'id':'hd','refreshRate':60,'size':{'width':1920,'height':1080}}]}

    def test_restores_after_temporary_failure(self):
        run = Mock(side_effect=[subprocess.CalledProcessError(1, 'kscreen-doctor'), None])
        with self.assertRaises(subprocess.CalledProcessError):
            manual.cycle(self.output(), run=run, sleep=Mock())
        self.assertEqual(run.call_args_list[-1].args[0], ['kscreen-doctor','output.HDMI-A-1.mode.1'])

    def test_preserves_initial_mode_after_standard_fallback(self):
        run, sleep = Mock(), Mock()
        manual.cycle(self.output(), run=run, sleep=sleep)
        self.assertEqual([c.args[0][-1] for c in run.call_args_list], ['output.HDMI-A-1.mode.hd','output.HDMI-A-1.mode.1'])
        sleep.assert_called_once_with(5)

    def test_no_alternate_does_not_change_display(self):
        output = self.output();output['modes'] = output['modes'][:2]
        run = Mock()
        with self.assertRaises(RuntimeError):manual.cycle(output, run=run)
        run.assert_not_called()

if __name__ == '__main__':unittest.main()
