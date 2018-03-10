# wechat-pa-subscribe
Get the newest ten articles of a Wechat Public Account with help of Sogou Wechat Search Engine.

Just `python update.py` and all of the ten articles are cached:
```
$ python update.py 
INFO:root:Article[1] 2018年3月10日 - 记录 _ 华附国际部“创必承国际精英奖学金”签约仪式
INFO:root:Article[2] 2018年3月9日 - 原创 学生故事一 _ 堂吉诃德在洛克王国
INFO:root:Article[4] 2018年3月7日 - Hi~这是一份华附AP插班报考指南
INFO:root:Article[6] 2018年3月2日 - 就在下周，华附国际部IFY学生将与英国14所大学招生官面谈
INFO:root:Article[8] 2018年2月28日 - 千呼万唤始出来 _ 2018华附AP首场入学考试定于4月14日开考
INFO:root:Article[10] 2018年2月27日 - HFI→NYU→匹兹堡 _ 郝贝诗：我的本科直升博士之路
$ python update.py 
INFO:root:Article[1] 2018年3月10日 - 记录 _ 华附国际部“创必承国际精英奖学金”签约仪式
INFO:root:Article[2] 2018年3月9日 - 原创 学生故事一 _ 堂吉诃德在洛克王国
INFO:root:Article[3] 2018年3月8日 - 大学到访 _ 今天来访的不只有英国大学招生官，还有英国的天气……
INFO:root:Article[5] 2018年3月5日 - 祝贺HFI陈博远同学获2018英国化学奥赛全球金奖！
INFO:root:Article[7] 2018年3月2日 - 看！这里有EAP学生作品展，还有“春盎然”结业派对！
INFO:root:Article[9] 2018年2月28日 - 今年元宵怎么过？——本周四晚一楼大堂见！
$ python update.py 
INFO:root:Article[1] 2018年3月10日 - 记录 _ 华附国际部“创必承国际精英奖学金”签约仪式
INFO:root:Article[2] 2018年3月9日 - 原创 学生故事一 _ 堂吉诃德在洛克王国
INFO:root:Article[4] 2018年3月7日 - Hi~这是一份华附AP插班报考指南
INFO:root:Article[6] 2018年3月2日 - 就在下周，华附国际部IFY学生将与英国14所大学招生官面谈
INFO:root:Article[8] 2018年2月28日 - 千呼万唤始出来 _ 2018华附AP首场入学考试定于4月14日开考
INFO:root:Article[10] 2018年2月27日 - HFI→NYU→匹兹堡 _ 郝贝诗：我的本科直升博士之路
$ python update.py 
INFO:root:Article[1] 2018年3月10日 - 记录 _ 华附国际部“创必承国际精英奖学金”签约仪式
INFO:root:Article[2] 2018年3月9日 - 原创 学生故事一 _ 堂吉诃德在洛克王国
INFO:root:Article[3] 2018年3月8日 - 大学到访 _ 今天来访的不只有英国大学招生官，还有英国的天气……
INFO:root:Article[5] 2018年3月5日 - 祝贺HFI陈博远同学获2018英国化学奥赛全球金奖！
INFO:root:Article[7] 2018年3月2日 - 看！这里有EAP学生作品展，还有“春盎然”结业派对！
INFO:root:Article[9] 2018年2月28日 - 今年元宵怎么过？——本周四晚一楼大堂见！
$ cd mirror/
$ ls
HFI2004
$ cd HFI2004/
$ ls
2018年2月27日 - HFI→NYU→匹兹堡 _ 郝贝诗：我的本科直升博士之路
2018年2月28日 - 今年元宵怎么过？——本周四晚一楼大堂见！
2018年2月28日 - 千呼万唤始出来 _ 2018华附AP首场入学考试定于4月14日开考
2018年3月10日 - 记录 _ 华附国际部“创必承国际精英奖学金”签约仪式
2018年3月2日 - 就在下周，华附国际部IFY学生将与英国14所大学招生官面谈
2018年3月2日 - 看！这里有EAP学生作品展，还有“春盎然”结业派对！
2018年3月5日 - 祝贺HFI陈博远同学获2018英国化学奥赛全球金奖！
2018年3月7日 - Hi~这是一份华附AP插班报考指南
2018年3月8日 - 大学到访 _ 今天来访的不只有英国大学招生官，还有英国的天气……
2018年3月9日 - 原创 学生故事一 _ 堂吉诃德在洛克王国
```

# Requirements

* Python3
* Python3 Library Seleium

```keyboard
# sudo apt-get install python3
# sudo pip install selenium
```

* Chrome
* [Chrome Driver](npm.taobao.org/mirrors/chromedriver/). Remember to choose the right version that works with the version of installed Chrome.
