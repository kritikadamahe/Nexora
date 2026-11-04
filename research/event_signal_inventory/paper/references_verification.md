# Reference verification log

Verification sources: DOI metadata was retrieved from doi.org content negotiation (Crossref CSL-JSON) and/or the OpenAlex API (`api.openalex.org/works/doi:...`), checking title, authors, venue, volume, issue, pages and print year. Entries without a DOI were checked on the publisher or official proceedings page.

## Verified entries

| key | how verified | why cited |
|---|---|---|
| nahmias1982perishable | doi:10.1287/opre.30.4.680 (Crossref, OpenAlex) | Foundational review of perishable inventory theory. |
| koenker1978regression | doi:10.2307/1913643 (Crossref, OpenAlex; Econometric Society page gives pp. 33--50) | Quantile regression, basis of the quantile forecasts. |
| friedman2001gbm | doi:10.1214/aos/1013203451 (OpenAlex) | Gradient boosting machine used by every forecasting arm. |
| pedregosa2011sklearn | https://jmlr.org/papers/v12/pedregosa11a.html (JMLR page: 16 authors, vol. 12, no. 85, pp. 2825--2830) | Software used (HistGradientBoostingRegressor). |
| holm1979simple | JSTOR stable URL https://www.jstor.org/stable/4615733 (vol. 6, no. 2, pp. 65--70; no DOI) | Holm multiple-testing correction. |
| efron1993bootstrap | doi:10.1007/978-1-4899-4541-9 (Crossref: Efron & Tibshirani, 1993) | Bootstrap intervals. |
| makridakis2022m5 | doi:10.1016/j.ijforecast.2021.11.013 (Crossref, OpenAlex) | M5 accuracy competition; tree-based (LightGBM) methods dominated. |
| favorita2018kaggle | https://www.kaggle.com/c/favorita-grocery-sales-forecasting (page title confirmed) | Favorita data set. |
| nandakumar1993near | doi:10.1287/mnsc.39.12.1490 (OpenAlex) | Near-myopic heuristics for fixed-life perishable ordering. |
| broekmeulen2009heuristic | doi:10.1016/j.cor.2009.01.017 (OpenAlex) | Practical perishable heuristic with lead time and time-varying demand, close to our setting. |
| bakker2012review | doi:10.1016/j.ejor.2012.03.004 (OpenAlex) | Survey of deteriorating-inventory models 2001--2011. |
| janssen2016literature | doi:10.1016/j.ijpe.2016.08.019 (OpenAlex, Crossref) | Survey of deteriorating-inventory models 2012--2015. |
| haijema2019improved | doi:10.1016/j.ijpe.2018.03.008 (OpenAlex; Crossref print issue 2019) | Value of stock-age information in perishable ordering (our policy uses age-aware FIFO stock). |
| fildes2022retail | doi:10.1016/j.ijforecast.2019.06.004 (Crossref; print 2022, vol. 38(4)) | Review of retail forecasting incl. calendar/promotion effects. |
| trapero2015identification | doi:10.1057/jors.2013.174 (Crossref; print 2015, vol. 66(2)) | Promotional sales forecasting models. |
| vandonselaar2016analysis | doi:10.1016/j.ijpe.2015.10.022 (Crossref; print 2016) | Promotion demand forecasting specifically for perishables. |
| huber2020daily | doi:10.1016/j.ijforecast.2020.02.005 (Crossref, OpenAlex) | ML retail demand forecasting focused on calendric special days. |
| makridakis2022m5background | doi:10.1016/j.ijforecast.2021.07.007 (Crossref) | Describes M5 data incl. event calendar and SNAP days. |
| steinker2017value | doi:10.1111/poms.12721 (OpenAlex) | External (weather) signals in retail demand forecasting and operations. |
| gardner1990evaluating | doi:10.1287/mnsc.36.4.490 (OpenAlex) | Classic argument that forecasts should be judged by inventory performance. |
| kourentzes2020optimising | doi:10.1016/j.ijpe.2019.107597 (Crossref; print 2020, vol. 225, article 107597) | Accuracy metrics vs inventory outcomes; optimising forecasts for inventory. |
| ban2019big | doi:10.1287/opre.2018.1757 (Crossref; print 2019) | Feature-based (big-data) newsvendor. |
| huber2019data | doi:10.1016/j.ejor.2019.04.043 (Crossref) | Data-driven newsvendor with ML/quantile approaches on bakery data. |
| bertsimas2020predictive | doi:10.1287/mnsc.2018.3253 (Crossref; print 2020) | Predictive-to-prescriptive analytics with ML covariates. |
| ke2017lightgbm | NeurIPS proceedings (neurips.cc poster 9099; proceedings metadata pp. 3146--3154; no DOI) | LightGBM, the GBDT library behind leading M5 entries. |
| bishop1995training | doi:10.1162/neco.1995.7.1.108 (OpenAlex) | Input-noise injection as regularisation; basis of arm D. |
| quinonero2009dataset | doi:10.7551/mitpress/9780262170055.001.0001 (Crossref: editors, MIT Press; release dated 12 Dec 2008, library catalogues give (c)2009) | Dataset shift between training and deployment. |
| vapnik2009new | doi:10.1016/j.neunet.2009.06.042 (OpenAlex) | Learning using privileged information (training-only information); contrast with clean-calendar training. |
| wen2021time | doi:10.24963/ijcai.2021/631 (OpenAlex) | Survey of time-series data augmentation. |
| kaufman2012leakage | doi:10.1145/2382577.2382579 (OpenAlex: vol. 6, no. 4, 21 pp.) | Leakage of information unavailable at prediction time. |

Total: 30 verified entries (8 original + 22 new).

## Corrections to the 8 original entries

- nahmias1982perishable: added missing issue `number = {4}` and DOI.
- koenker1978regression, friedman2001gbm, makridakis2022m5: no errors; DOIs added.
- pedregosa2011sklearn: replaced `and others` with the full 16-author list from the JMLR page; added `number = {85}` and URL.
- holm1979simple: no errors; JSTOR stable URL added (paper has no DOI).
- efron1993bootstrap: no errors; added series (Monographs on Statistics and Applied Probability, 57) and DOI (the DOI is the Springer-hosted record of the same 1993 book).
- favorita2018kaggle: no errors in the fields; URL resolves to the competition page. The page does not print a year; the competition ran Oct 2017 to Jan 2018, so 2018 (close) is defensible, but some papers cite it as 2017.

## Verified but left out of the list (to keep it near 30)

All of these resolved correctly and can be added if a reviewer asks:

- Chen, Pang & Pan (2014), Operations Research 62(2):284--300, doi:10.1287/opre.2014.1261 (perishable pricing + inventory; off-topic).
- Chao, Gong, Shi & Zhang (2015), Operations Research 63(3):585--601, doi:10.1287/opre.2015.1386 (approximation algorithms for perishables).
- Nahmias (2011), Perishable Inventory Systems, Springer, doi:10.1007/978-1-4419-7999-5.
- Huang, Fildes & Soopramanien (2014), EJOR 237(2):738--748, doi:10.1016/j.ejor.2014.02.022.
- Ma, Fildes & Huang (2016), EJOR 249(1):245--257, doi:10.1016/j.ejor.2015.08.029.
- Ali, Sayın, van Woensel & Fransoo (2009), Expert Systems with Applications 36(10):12340--12348, doi:10.1016/j.eswa.2009.04.052.
- Makridakis et al. (2022), M5 uncertainty competition, IJF 38(4):1365--1385, doi:10.1016/j.ijforecast.2021.10.009.
- Sanders & Graman (2009), Omega 37(1):116--125, doi:10.1016/j.omega.2006.10.004.
- Syntetos, Babai & Gardner (2015), J. Business Research 68(8):1746--1752, doi:10.1016/j.jbusres.2015.03.034.
- Prak & Teunter (2019), IJF 35(1):224--238, doi:10.1016/j.ijforecast.2017.11.004.
- Petropoulos et al. (2022), Forecasting: theory and practice, IJF 38(3):705--871, doi:10.1016/j.ijforecast.2021.11.001.
- Taylor (2007), EJOR 178(1):154--167, doi:10.1016/j.ejor.2006.02.006.
- Ulrich et al. (2021), EJOR 294(3):831--842, doi:10.1016/j.ejor.2019.11.029.
- Gneiting & Raftery (2007), JASA 102(477):359--378, doi:10.1198/016214506000001437.
- Januschowski et al. (2022), Forecasting with trees, IJF 38(4):1473--1481, doi:10.1016/j.ijforecast.2021.10.004.
- Moreno-Torres et al. (2012), Pattern Recognition 45(1):521--530, doi:10.1016/j.patcog.2011.06.019.
- Frénay & Verleysen (2014), IEEE TNNLS 25(5):845--869, doi:10.1109/TNNLS.2013.2292894 (label noise; our noise is in inputs).
- Iwana & Uchida (2021), PLoS ONE 16(7):e0254841, doi:10.1371/journal.pone.0254841.
- Globerson & Roweis (2006), "Nightmare at test time", ICML, pp. 353--360, doi:10.1145/1143844.1143889.
- Cameron, Gelbach & Miller (2008), RESTAT 90(3):414--427, doi:10.1162/rest.90.3.414 (useful if the paper discusses few-cluster inference).
- Good (2005), Permutation, Parametric and Bootstrap Tests of Hypotheses, Springer, doi:10.1007/b138696 (for the sign-flip test).


## Added 2026-11-05 (17 entries, from the list above)

Metadata for each entry was generated from its Crossref record (title, authors, journal, volume, issue, pages, year), with author names checked in OpenAlex where Crossref was incomplete.

| key | how verified | why cited |
|---|---|---|
| nahmias2011perishable | doi:10.1007/978-1-4419-7999-5 (Crossref; OpenAlex) | Book-length treatment of perishable inventory, alongside the 1982 review. |
| petropoulos2022forecasting | doi:10.1016/j.ijforecast.2021.11.001 (Crossref; OpenAlex) | Broad review of forecasting theory and practice; listed as first author and others (80 authors). |
| ali2009sku | doi:10.1016/j.eswa.2009.04.052 (Crossref; OpenAlex) | SKU demand forecasting under promotions. |
| huang2014value | doi:10.1016/j.ejor.2014.02.022 (Crossref; OpenAlex) | Competitive and promotional information in FMCG sales forecasting. |
| ma2016demand | doi:10.1016/j.ejor.2015.08.029 (Crossref; OpenAlex) | High-dimensional promotional information in SKU retail forecasting. |
| januschowski2022forecasting | doi:10.1016/j.ijforecast.2021.10.004 (Crossref; OpenAlex) | Why tree-based models did well in M5. |
| makridakis2022m5uncertainty | doi:10.1016/j.ijforecast.2021.10.009 (Crossref; OpenAlex) | M5 quantile-forecast track. |
| sanders2009quantifying | doi:10.1016/j.omega.2006.10.004 (Crossref; OpenAlex) | Operational cost of forecast errors; full author names from OpenAlex (Crossref gives initials only). |
| prak2019general | doi:10.1016/j.ijforecast.2017.11.004 (Crossref; OpenAlex) | Forecast uncertainty in inventory models. |
| taylor2007forecasting | doi:10.1016/j.ejor.2006.02.006 (Crossref; OpenAlex) | Quantile regression for daily supermarket sales. |
| ulrich2021distributional | doi:10.1016/j.ejor.2019.11.029 (Crossref; OpenAlex) | Distributional demand forecasts in e-grocery. |
| gneiting2007strictly | doi:10.1198/016214506000001437 (Crossref; OpenAlex) | Proper scoring rules, including the pinball loss. |
| morenotorres2012unifying | doi:10.1016/j.patcog.2011.06.019 (Crossref; OpenAlex) | Definitions of dataset shift. |
| globerson2006nightmare | doi:10.1145/1143844.1143889 (Crossref; OpenAlex) | Robustness to features deleted at test time, analogous to missed announcements. |
| iwana2021empirical | doi:10.1371/journal.pone.0254841 (Crossref; OpenAlex) | Time-series data augmentation, alongside Wen et al. |
| good2005permutation | doi:10.1007/b138696 (Crossref; OpenAlex) | Permutation (sign-flip) tests; author from OpenAlex (Crossref record has none). |
| cameron2008bootstrap | doi:10.1162/rest.90.3.414 (Crossref; OpenAlex) | Cluster bootstrap understates uncertainty with few clusters. |

## Dropped because not verified

- None of the requested candidates failed. Social-media/news signals for retail demand (thread 8) were not added: no peer-reviewed source was checked within this pass, so only weather information (Steinker et al. 2017) is cited.
