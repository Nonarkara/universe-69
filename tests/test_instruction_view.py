"""Instruction labels describe only valid, person-specific active contracts."""
import json
from pathlib import Path
import shutil
import subprocess
import unittest

ROOT = Path(__file__).resolve().parents[1]
NODE = shutil.which('node')


@unittest.skipUnless(NODE, 'Node is a workbench-only viewer test runner')
class TestInstructionView(unittest.TestCase):
    def label(self, expression):
        src = (ROOT / 'web/index.html').read_text()
        self.assertTrue('function instructionActivity(' in src, 'Instruction helper missing')
        helpers = src[src.index('// ---- local camp state'):src.index('// ---- LAGOON ---')]
        result = subprocess.run([NODE, '-e', helpers + '\nprocess.stdout.write(JSON.stringify(' + expression + '));'],
                                check=True, capture_output=True, text=True)
        return json.loads(result.stdout)

    def test_roles_and_topics_have_plain_labels(self):
        self.assertEqual(self.label("[instructionActivity({instruction:{7:{role:'seeking',tech:'fishing',other:8}}},7),instructionActivity({instruction:{8:{role:'teaching',tech:'stone_tools',other:7}}},8)]"),
                         ['seeking fishing instruction', 'explaining stone tools'])

    def test_legacy_empty_and_other_person_stay_unlabelled(self):
        self.assertEqual(self.label("[instructionActivity({},7),instructionActivity({instruction:{}},7),instructionActivity({instruction:{8:{role:'seeking',tech:'fire',other:7}}},7)]"), ['', '', ''])

    def test_unknown_roles_topics_and_malformed_partners_are_rejected(self):
        self.assertEqual(self.label("[{role:'finished',tech:'fire',other:8},{role:'seeking',tech:'<i>magic</i>',other:8},{role:'teaching',tech:'toString',other:8},{role:'seeking',tech:'fire',other:null},{role:'seeking',tech:'fire',other:7}].map(function(x){return instructionActivity({instruction:{7:x}},7);})"), ['', '', '', '', ''])

    def test_existing_person_details_and_diary_use_instruction(self):
        src = (ROOT / 'web/index.html').read_text()
        helpers = src[src.index('// ---- local camp state'):src.index('// ---- LAGOON ---')]
        people = src[src.index('var diary={'):src.index('function hudText(')]
        setup = "var sel={e:7,l:0},actors6={7:{id:7,act:1,moving:true}},actors9={},ACT_LABEL=['idle','walking'],state={events:[],u:{eden:{year:2,day:720,detail:{7:['Ada',24,1,0,1,2,0,0]},instruction:{7:{role:'seeking',tech:'fishing',other:8}}}}};"
        js = helpers + setup + people + "keepDiary('e',state.u.eden);process.stdout.write(JSON.stringify([whoInfo('e').act,diary.e[0]]));"
        result = json.loads(subprocess.run([NODE, '-e', js], check=True, capture_output=True, text=True).stdout)
        self.assertEqual(result, ['seeking fishing instruction', 'Y2 d0 · seeking fishing instruction'])

    def test_cleared_intent_restores_existing_craft_and_diary(self):
        src = (ROOT / 'web/index.html').read_text()
        helpers = src[src.index('// ---- local camp state'):src.index('// ---- LAGOON ---')]
        people = src[src.index('var diary={'):src.index('function hudText(')]
        setup = "var sel={e:7,l:0},actors6={7:{id:7,act:0,moving:false}},actors9={},ACT_LABEL=['idle'],state={events:[],u:{eden:{year:2,day:720,detail:{7:['Ada',24,1,0,1,2,0,0]},crafts:{7:'writing'},instruction:{7:{role:'teaching',tech:'fire',other:8}}}}};"
        js = helpers + setup + people + "keepDiary('e',state.u.eden);state.u.eden.instruction={};keepDiary('e',state.u.eden);process.stdout.write(JSON.stringify([whoInfo('e').act,diary.e]));"
        result = json.loads(subprocess.run([NODE, '-e', js], check=True, capture_output=True, text=True).stdout)
        self.assertEqual(result, ['making records', ['Y2 d0 · explaining fire', 'Y2 d0 · making records']])

    def test_compact_hud_uses_world_width_without_duplicate_instruction(self):
        src = (ROOT / 'web/index.html').read_text()
        hud = src[src.index('function hudText('):src.index('function refreshHud(')]
        setup = "var window={innerWidth:1024},width=512,document={getElementById:function(){return {clientWidth:width};}},shots={},view={},hudExtra='';function whoInfo(){return {name:'Ada',act:'explaining stone tools',craft:'',instruction:'explaining stone tools'};}function escapeHTML(s){return String(s);}function doingHTML(){return '';}function statLine(){return '';}"
        js = setup + hud + "var u={phase:'living',year:1,pop:16};var compact=hudText(u,'l');width=720;var wide=hudText(u,'l');process.stdout.write(JSON.stringify([compact,wide]));"
        result = json.loads(subprocess.run([NODE, '-e', js], check=True, capture_output=True, text=True).stdout)
        self.assertIn('ADA', result[0])
        self.assertNotIn('EXPLAINING STONE TOOLS', result[0])
        self.assertIn('EXPLAINING STONE TOOLS', result[1])

    def test_all_current_topics_are_supported_without_claiming_mastery(self):
        topics = ['fire', 'stone_tools', 'fishing', 'predator_hunt', 'shelter', 'preservation', 'lore', 'agriculture', 'domestication', 'granary', 'seacraft', 'healing', 'metallurgy', 'writing']
        result = self.label(json.dumps(topics) + ".map(function(t){return instructionActivity({instruction:{7:{role:'teaching',tech:t,other:8}}},7);})")
        self.assertEqual(result, ['explaining ' + t.replace('_', ' ') for t in topics])
