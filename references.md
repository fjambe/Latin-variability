# References

### About parsing Latin:
* **CoNLL Shared Task 2018** on Multilingual Parsing from Raw Text to Universal Dependencies. Results here: https://universaldependencies.org/conll18/results-las.html.
* **CoNLL Shared Task 2017** on Multilingual Parsing from Raw Text to Universal Dependencies.

* [More Data and New Tools. Advances in Parsing the Index Thomisticus Treebank](http://ceur-ws.org/Vol-2989/long_paper20.pdf) (Gamba et al., 2021).
* [Differentia compositionem facit. A Slower-paced and Reliable Parser for Latin](https://aclanthology.org/L16-1108.pdf) (Ponti and Passarotti, 2016).  
Collapse of the parser performance on all the authors represented in the LDT compared to the results achieved on Thomas Aquinas’ texts, due to the remarkable incongruity holding between the varieties of Latin represented in the training set (IT-TB) and in the test data (LDT).  
* Parsing the Index Thomisticus Treebank. Some Preliminary Results (Passarotti and Ruffolo, 2010).  
Cf. “Although both the treebanks adopt the same annotation guidelines, it seems that the dissimilarity between the syntax of the texts in IT-TB and LDT data sets is so high that the data from one treebank cannot be used to train parsers to be applied on the other treebank data.”
*	[Improvements in Parsing the Index Thomisticus Treebank. Revision, Combination and a Feature Model for Medieval Latin](http://www.lrec-conf.org/proceedings/lrec2010/pdf/178_Paper.pdf) (Passarotti and Dell’Orletta, 2010).

* [Investigation of Transfer Languages for Parsing Latin: Italic Branch vs. Hellenic Branch](https://aclanthology.org/2021.nodalida-main.32.pdf) (Karamolegkou and Stymne, 2021).

### About Latin variability:
* **EvaLatin 2022**: lemmatisation, POS tagging and morphological features.
* **EvaLatin 2020**: [Overview of the EvaLatin 2020 Evaluation Campaign](http://aclanthology.lst.uni-saarland.de/2020.lt4hala-1.16.pdf) (Sprugnoli et al. 2020).  
Lemmatisation and POS tagging. Cross-genre and Cross-time subtasks to evaluate the portability of NLP tools for Latin across different genres and time periods, by analyzing the impact of genre-specific and diachronic features.  
Cf.: “All the systems suffer from the shift to a different genre or to a different time period with a drop in the performances which, in some cases, exceeds 10 points. Taking a more in-depth look at the results, we can notice that, in general, the participating systems perform better on the Medieval text by Thomas Aquinas than on the Classical poems by Horace in the Lemmatization task, whereas the opposite is true for the PoS tagging task.”   
  * [UDPipe at EvaLatin 2020: Contextualized Embeddings and Treebank Embeddings](https://aclanthology.org/2020.lt4hala-1.20.pdf) (Straka and Strakova, 2020).
  * [JHUBC’s Submission to LT4HALA EvaLatin 2020](https://aclanthology.org/2020.lt4hala-1.18.pdf) (Wu and Nicolai, 2020).
  * [A Gradient Boosting-Seq2Seq System for Latin POS Tagging and Lemmatization](https://aclanthology.org/2020.lt4hala-1.19.pdf) (Celano, 2020).
  * [Voting for POS Tagging of Latin Texts: Using the Flair of FLAIR to Better Ensemble Classifiers by Example of Latin](https://aclanthology.org/2020.lt4hala-1.21.pdf) (Stoeckel et al., 2020).
  * [Data-driven Choices in Neural Part-of-Speech Tagging for Latin](https://aclanthology.org/2020.lt4hala-1.17.pdf) (Bacon, 2020).

* [The Annotation of Liber Abbaci, a Domain-Specific Latin Resource](http://ceur-ws.org/Vol-3033/paper24.pdf) (Grotto et al., 2021).  
 Variability wrt lemmatisation and POS tagging, cf.: “The results of existing UDPipe models in lemmatization and tagging show low accuracy and F1 scores when compared to the state of the art for these tasks in the recent EvaLatin 2020 evaluation campaign”.
*	[Improving Lemmatization of Non-Standard Languages with Joint Learning](https://aclanthology.org/N19-1153.pdf) (Manjavacas et al., 2019).  
Focus on historical languages, Medieval Latin included.
*	[Integrated Sequence Tagging for Medieval Latin Using Deep Representation Learning](https://arxiv.org/ftp/arxiv/papers/1603/1603.01597.pdf) (Kestemont and De Gussem, 2016).
* [Practitioner’s view: A comparison and a survey of lemmatization and morphological tagging in German and Latin](https://www.researchgate.net/publication/334382605_Practitioner's_view_A_comparison_and_a_survey_of_lemmatization_and_morphological_tagging_in_German_and_Latin) (Gleim et al., 2019).  
State of the art in 2019 about lemmatisation and tagging. Lower results are reported in case of out-of-domain data.


### Other:
* [Automatic discovery of Latin syntactic changes](https://aclanthology.org/W16-2120) (Elsner and Lane, 2016)
