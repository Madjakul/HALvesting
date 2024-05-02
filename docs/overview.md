# Overview

## Dataset Summary

HALvest is compriseed of fulltext from open papers found on [Hyper Articles en Ligne (HAL)](https://hal.science/). Our dump is mostly english/french but gather papers written in 34 languages across 13 domains.

You can download the dataset using Hugging Face datasets:
```py
from datasets import load_dataset

ds = load_dataset("Madjakul/HALvest", "en")
```

### Details

Building the dataset is a four steps process: data fetching from HAL, data merging, data enriching and data filtering.

1. We first request [HAL's API](https://api.archives-ouvertes.fr/docs) in order to gather open research papers and parse it -- effectively sorting papers by language. Then, we download the PDFs of the fetched data.
2. Using [GROBID](https://github.com/kermitt2/grobid), we convert each PDF to an `xml-tei` format in order to have structured data. We convert each `xml-tei` file to a `txt` format before concatenating it with the paper's.
3. We compute some statistics about each document.
4. We filter the data based of off simple ratios to expurge badly encoded documents.



### Languages

Every languages that do not have stop-words are removed from the clean dataset. Due to encoding problems, arabic is also removed from the clean dataset. Japanese and chinee are removed due to most of the heuristics used failing to filter out gibberish data on it.

ISO-639|Language|# Documents|# mT5 Tokens
-------|--------|-----------|--------
en|English|442,892|7,606,895,258
fr|French|193,437|8,728,722,255
es|Spanish|2,930|68,076,878
it|Italian|1,172|48,747,986
pt|Portuguese|934|32,918,832
de|German|646|11,699,417
ru|Russian|245|5,763,532
eu|Basque|112|2,297,460
pl|Polish|43|987,878
el|Greek|42|1,680,696
ro|Romanian|39|1,298,901
ca|Catalan|28|975,078
da|Danish|26|961,895
br|Breton|24|998,088
ko|Korean|17|226,268
tr|Turkish|17|149,718
hu|Hungarian|14|577,568
eo|Esperanto|14|105,286
fa|Persian|10|190,929
hy|Armenian|10|127,988
cs|Czech|9|712,263
bg|Bulgarian|8|180,146
id|Indonesian|9|53,075
he|Hebrew|8|61,283
hr|Croatian|8|40,621
et|Estonian|7|20,405
sv|Swedish|6|270,642
no|Norwegian|6|62,767
fi|Finnish|3|17,583
sw|Swahili|2|73,921
gl|Galician|2|29,688
th|Thai|1|70,909
sl|Slovenian|1|22,844
sk|Slovak|1|12,997


### Domains

Domain|Code|# Documents|# mT5 Tokens
------|----|-----------|------------
Humanities and Social Sciences|shs|152,818|5,487,738,344
Computer Science|info|143,229|2,436,890,715
Life Sciences|sdv|111,038|3,008,633,879
Engineering Sciences|spi|99,393|2,155,602,249
Physics|phys|63,557|1,435,905,328
Mathematics|math|54,393|1,359,277,656
Chemical Science|chim|38,500|857,617,219
Environmental Science|sde|30,827|566,560,266
Sciences of the Universe|sdu|22,917|654,909,131
Statistics|stat|20,571|1,449,842,318
Cognitive science|scco|11,584|222,832,732
Quantitative Finance|qfin|3,290|64,970,285
Nonlinear Sciences|nlin|1,908|29,296,684

You can browse through every domains and sub-domains here: [https://hal.science/browse/domain](https://hal.science/browse/domain).