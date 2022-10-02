import unittest

from podcast.pkg.segment.text_segments import TextSegment


class TextSegmentsTest(unittest.TestCase):
    def test_text_segments(self):
        text_segment = TextSegment("zh", "多年以后，奥雷连诺上校站在行刑队面前，准会想起父亲带他去参观冰块的那个遥远的下午。当时，马孔多是个二十户人家的村庄，一座座土房都盖在河岸上，河水清澈，沿着遍布石头的河床流去，河里的石头光滑、洁白，活象史前的巨蛋。这块天地还是新开辟的，许多东西都叫不出名字，不得不用手指指点点。每年三月，衣衫褴楼的吉卜赛人都要在村边搭起帐篷，在笛鼓的喧嚣声中，向马孔多的居民介绍科学家的最新发明。他们首先带来的是磁铁。一个身躯高大的吉卜赛人，自称梅尔加德斯，满脸络腮胡子，手指瘦得象鸟的爪子，向观众出色地表演了他所谓的马其顿炼金术士创造的世界第八奇迹。他手里拿着两大块磁铁，从一座农舍走到另一座农舍，大家都惊异地看见，铁锅、铁盆、铁钳、铁炉都从原地倒下，木板上的钉子和螺丝嘎吱嘎吱地拼命想挣脱出来，甚至那些早就丢失的东西也从找过多次的地方兀然出现，乱七八糟地跟在梅尔加德斯的魔铁后面。“东西也是有生命的，”吉卜赛人用刺耳的声调说，“只消唤起它们的灵性。”霍·阿·布恩蒂亚狂热的想象力经常超过大自然的创造力，甚至越过奇迹和魔力的限度，他认为这种暂时无用的科学发明可以用来开采地下的金子。")
        languages, text_segments = text_segment.gen_lang_segments()
        self.assertEqual(languages, set(["zh"]))


    def test_text_segments(self):
        with open("${HOME}/Desktop/百年孤独.txt", "r") as f:
            content = f.read()
            text_segment = TextSegment("zh", content)
            languages, text_segments = text_segment.gen_lang_segments()
            self.assertEqual(languages, set(["zh"]))

    def test_percent_segments(self):
        text_segment = TextSegment("zh", "50.45%人员即将失业。")
        languages, text_segments = text_segment.gen_lang_segments()
        self.assertEqual(languages, set(["zh"]))
