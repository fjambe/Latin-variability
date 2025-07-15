# Script to train the hm-proiel model with UDPipe 1.2
# No tokenizer is trained
# fastText embeddings
# Parameters are set according to UD 2.5 Models reproducible training, both for tagger and parser
# The harmonised version of PROIEL_train is used

UDPIPE_PATH=/lnet/work/people/gamba/UDPipe
MODEL_OUTPUT=/lnet/work/people/gamba/UDPipe/udp-harmonisation/HM-udp-models/hm-proiel.udpipe
FASTTEXT_VEC=/lnet/work/people/gamba/sz-training/stanza/fasttext/Latin/cc.la.300.vec
TRAIN_DATA=/lnet/work/people/gamba/GitHub/harmonization/harmonized-treebanks/UD_Latin-PROIEL/HM-la_proiel-ud-train.conllu

# Run UDPipe training
$UDPIPE_PATH --train $MODEL_OUTPUT \
  --tokenizer=none \
  --tagger='models=2;templates_1=tagger;guesser_suffix_rules_1=8;guesser_enrich_dictionary_1=6;guesser_prefixes_max_1=0;use_lemma_1=0;use_xpostag_1=1;use_feats_1=1;provide_lemma_1=0;provide_xpostag_1=1;provide_feats_1=1;prune_features_1=0;templates_2=lemmatizer;guesser_suffix_rules_2=8;guesser_enrich_dictionary_2=6;guesser_prefixes_max_2=4;use_lemma_2=1;use_xpostag_2=0;use_feats_2=0;provide_lemma_2=1;provide_xpostag_2=0;provide_feats_2=0;prune_features_2=0' \
  --parser='iterations=30;embedding_upostag=20;embedding_feats=20;embedding_xpostag=0;embedding_form=50;embedding_form_file=/home/gamba/stanza/fasttext/Latin/cc.la.300.vec;embedding_lemma=0;embedding_deprel=20;learning_rate=0.01;learning_rate_final=0.001;l2=0.5;hidden_layer=200;batch_size=10;transition_system=link2;transition_oracle=static;structured_interval=8' \
  $TRAIN_DATA

