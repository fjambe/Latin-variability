#!/usr/bin/env perl
# Compares Latin test sets before and after harmonization.
# Copyright © 2023 Dan Zeman <zeman@ufal.mff.cuni.cz>
# License: GNU GPL

use utf8;
use open ':utf8';
binmode(STDIN, ':utf8');
binmode(STDOUT, ':utf8');
binmode(STDERR, ':utf8');
use Getopt::Long;

sub usage
{
    print STDERR ("Usage: compare_latin.pl [conllu|wcc]\n");
    print STDERR ("    Detailed comparison of Latin treebanks and parser outputs before and after harmonization.\n");
    print STDERR ("    All test files should have the same number of sentences. Tokenization may differ but not\n");
    print STDERR ("    too much, as only those sentences will be compared that have the same number of nodes.\n");
    print STDERR ("    The script takes CoNLL-U test files from hard-coded paths on the ÚFAL network.\n");
    print STDERR ("    By default it prints the summary.\n");
    print STDERR ("    deprel ... Prints a detailed summary: deprels included in category labels where appropriate.\n");
    print STDERR ("    conllu ... Prints a CoNLL-U file where the comparison is annotated in the MISC column.\n");
    print STDERR ("    wcc ...... Prints the sentence/word statistics for each file and exits.\n");
    print STDERR ("    --help ... Prints this usage information and exits.\n");
    print STDERR ("Tip:\n");
    print STDERR ("    compare_latin.pl conllu | udapy -TMX print_comments=1 -X attributes=ord,form,upos,deprel,misc -X layout=compact util.Mark node='node.misc[\"Eval\"] == \"GLD=SYS-D\"' | less -R\n");
}

my $help = 0;
my $output = 'summary';
GetOptions
(
    'help' => \$help
);
if($help)
{
    usage();
    exit;
}
if($ARGV[0] =~ m/^(deprel|conllu|wcc)$/i)
{
    $output = lc($ARGV[0]);
}

# /net/work/people/gamba/UDPipe/UD-devbranch … gold standard before harmonization
# /net/work/people/gamba/GitHub/harmonization/harmonized-treebanks … gold standard after harmonization
# /net/work/people/gamba/stanza_initial/outputs_by_stanza/stanza_long-models … Stanza parser output before harmonization, LLCT and UDante
# /net/work/people/gamba/stanza_initial/outputs_by_stanza/stanza_pretrained … Stanza parser output after harmonization, ITTB, PROIEL and Perseus
# /net/work/people/gamba/UDPipe/initial_parsed_udp_outputs … UDPipe parser output before harmonization
# /net/work/people/gamba/UDPipe/udp-harmonisation/udp-hm-parsed-testdata … UDPipe parser output after harmonization

my %path;
$path{gold}{before} = '/net/work/people/gamba/UDPipe/UD-devbranch'; # subfolders: UD_Latin-{ITTB,LLCT,PROIEL,Perseus,UDante}-dev / la_ittb-ud-test.conllu
$path{gold}{after}  = '/net/work/people/gamba/GitHub/harmonization/harmonized-treebanks'; # subfolders standard names (without "-dev") but files are / HM-la_ittb-ud-test.conllu
$path{udpipe}{before} = '/net/work/people/gamba/UDPipe/initial_parsed_udp_outputs'; # no subfolders, directly files: udp-initial-ittb-by-ittb.conllu
$path{udpipe}{after}  = '/net/work/people/gamba/UDPipe/udp-harmonisation/udp-hm-parsed-testdata'; # no subfolders, directly files: udp-ittb-by-ittb.conllu
$path{stanza}{before}{1} = '/net/work/people/gamba/stanza_initial/outputs_by_stanza/stanza_long-models'; # no subfolders, directly files: stanza_ittb-by-llct-model.conllu
$path{stanza}{before}{2} = '/net/work/people/gamba/stanza_initial/outputs_by_stanza/stanza_pretrained'; # no subfolders, directly files: stanza_ittb-by-ittb-model.conllu
$path{stanza}{after} = '/net/work/people/gamba/sz-training/stanza/output_HM_conllus';

my @treebanks = qw(ittb llct proiel perseus udante);
my %captreebanks = ('ittb' => 'ITTB', 'llct' => 'LLCT', 'proiel' => 'PROIEL', 'perseus' => 'Perseus', 'udante' => 'UDante');
my %testfile;
foreach my $stage (qw(before after))
{
    foreach my $parser (qw(gold udpipe stanza))
    {
        if($parser eq 'gold')
        {
            foreach my $treebank (@treebanks)
            {
                if($stage eq 'before')
                {
                    # For real parsers, we have two levels: {$parser}{$model}.
                    $testfile{$stage}{$parser}{$parser}{$treebank} = $path{$parser}{$stage}.'/UD_Latin-'.$captreebanks{$treebank}.'-dev/la_'.$treebank.'-ud-test.conllu';
                }
                else # after
                {
                    # For real parsers, we have two levels: {$parser}{$model}.
                    $testfile{$stage}{$parser}{$parser}{$treebank} = $path{$parser}{$stage}.'/UD_Latin-'.$captreebanks{$treebank}.'/HM-la_'.$treebank.'-ud-test.conllu';
                }
            }
        }
        else # real parsers
        {
            foreach my $model (@treebanks)
            {
                foreach my $treebank (@treebanks)
                {
                    if($parser eq 'udpipe')
                    {
                        my $initial = $stage eq 'before' ? '-initial' : '';
                        $testfile{$stage}{$parser}{$model}{$treebank} = $path{$parser}{$stage}.'/udp'.$initial.'-'.$treebank.'-by-'.$model.'.conllu';
                    }
                    else # stanza
                    {
                        if($stage eq 'before')
                        {
                            if($model =~ m/^(llct|udante)$/)
                            {
                                $testfile{$stage}{$parser}{$model}{$treebank} = $path{$parser}{$stage}{1}.'/stanza_'.$treebank.'-by-'.$model.'-model.conllu';
                            }
                            else
                            {
                                $testfile{$stage}{$parser}{$model}{$treebank} = $path{$parser}{$stage}{2}.'/stanza_'.$treebank.'-by-'.$model.'-model.conllu';
                            }
                        }
                        else # after
                        {
                            $testfile{$stage}{$parser}{$model}{$treebank} = $path{$parser}{$stage}.'/stanza_'.$treebank.'-by-'.$model.'_hm-model.conllu';
                        }
                    }
                }
            }
        }
    }
}
# Check that all the files exist.
# Now the test treebank is the top-level loop because we want to see the same
# test data next to each other.
my $n = 0;
if($output eq 'wcc')
{
    foreach my $treebank (@treebanks)
    {
        foreach my $stage (qw(before after))
        {
            foreach my $parser (qw(gold udpipe stanza))
            {
                my @models = sort(keys(%{$testfile{$stage}{$parser}}));
                foreach my $model (@models)
                {
                    my $testfile = $testfile{$stage}{$parser}{$model}{$treebank};
                    if(-f $testfile)
                    {
                        my $label = "$treebank $parser $model $stage";
                        $label .= ' ' x (30-length($label));
                        print($label.`wc_conll.pl $testfile`);
                        $n++;
                    }
                    else
                    {
                        print("WARNING: '$testfile' does not exist.\n");
                    }
                }
            }
        }
    }
    print("Checked $n files.\n");
}
else
{
    foreach my $treebank (@treebanks)
    {
        print("----------------------------------------------------------------------------------------------------\n") unless($output eq 'conllu');
        foreach my $parser (qw(gold udpipe stanza))
        {
            my @models = sort(keys(%{$testfile{'before'}{$parser}}));
            foreach my $model (@models)
            {
                my $label = "$treebank $parser by$model before-after";
                $label .= ' ' x (40-length($label));
                my $parse0 = $testfile{'before'}{$parser}{$model}{$treebank};
                my $parse1 = $testfile{'after'}{$parser}{$model}{$treebank};
                my $gold0 = $testfile{'before'}{'gold'}{'gold'}{$treebank};
                my $gold1 = $testfile{'after'}{'gold'}{'gold'}{$treebank};
                compare_files($label, $parse0, $parse1, $gold0, $gold1, $output);
            }
        }
    }
    if($output ne 'conllu')
    {
        print("----------------------------------------------------------------------------------------------------\n");
        #my $evaluation = join(', ', map {"$totalnt{$_} $_"} (sort(keys(%totalnt))));
        my $evaluation = join(', ', map {"$totalnt{$_} $_"} (sort {my $r = $totalnt{$b} <=> $totalnt{$a}; unless($r) {$r = $a cmp $b} $r} (keys(%totalnt))));
        print("SUMMARY TOTAL: $evaluation\n");
    }
}



#------------------------------------------------------------------------------
# Compares two versions of the same test file.
#------------------------------------------------------------------------------
sub compare_files
{
    my $label = shift;
    my $file1 = shift;
    my $file2 = shift;
    my $gold1 = shift;
    my $gold2 = shift;
    my $output = shift;
    my @doc1 = read_conllu($file1);
    my @doc2 = read_conllu($file2);
    my @gdoc1 = read_conllu($gold1);
    my @gdoc2 = read_conllu($gold2);
    my $ns1 = scalar(@doc1);
    my $ns2 = scalar(@doc2);
    if($ns1 != $ns2)
    {
        print("WARNING: Unmatched number of sentences: $file1 $ns1, $file2 $ns2\n");
        return;
    }
    my $ns_compared = 0;
    my %nt;
    for(my $i = 0; $i < $ns1; $i++)
    {
        my @sentence1 = @{$doc1[$i]};
        my @sentence2 = @{$doc2[$i]};
        my @gsentence1 = @{$gdoc1[$i]};
        my @gsentence2 = @{$gdoc2[$i]};
        my $nt1 = scalar(@sentence1);
        my $nt2 = scalar(@sentence2);
        my $ngt1 = scalar(@gsentence1);
        my $ngt2 = scalar(@gsentence2);
        # Skip sentences that do not have identical number of tokens. This can
        # happen because harmonization occasionally changes tokenization.
        next if($nt1 != $nt2 || $nt1 != $ngt1 || $nt1 != $ngt2);
        $ns_compared++;
        print("\# $label\n") if($output eq 'conllu');
        for(my $j = 0; $j < $nt1; $j++)
        {
            my @f1 = split(/\t/, $sentence1[$j]);
            my @f2 = split(/\t/, $sentence2[$j]);
            my @gf1 = split(/\t/, $gsentence1[$j]);
            my @gf2 = split(/\t/, $gsentence2[$j]);
            # gold unchanged, parse unchanged (good or bad): NOCHANGE
            # gold unchanged, parse changed deprel, still bad: GLD=SYS=D0
            # gold unchanged, parse changed parent, still bad: GLD=SYS=0
            # gold unchanged, parse fixed deprel (same good parent): GLD=SYS+D
            # gold unchanged, parse fixed parent (same good deprel): GLD=SYS+P
            # gold unchanged, parse fixed parent and deprel: GLD=SYS+PD
            # gold unchanged, parse fixed parent but deprel is bad: GLD=SYS+P
            # gold unchanged, parse spoiled deprel (same good parent): GLD=SYS-D
            # gold unchanged, parse spoiled parent (same good deprel): GLD=SYS-P
            # gold unchanged, parse spoiled parent (regardless deprel): GLD=SYS-PD
            # gold changed deprel, parse correct before and after: GLD!D!SYS=1
            # gold changed deprel, parse wrong before and after (same or different error): GLD!D!SYS=0
            # gold changed deprel, parse fixed deprel (same good parent): GLD!D!SYS+D
            # gold changed deprel, parse fixed parent and deprel: GLD!D!SYS+PD
            # gold changed deprel, parse spoiled deprel (same good parent): GLD!D!SYS-D
            # gold changed deprel, parse spoiled parent (regardless deprel): GLD!D!SYS-PD
            # gold changed parent, parse correct before and after: GLD!PD!SYS=1
            # gold changed parent, parse wrong before and after (same or different error): GLD!PD!SYS=0
            # gold changed parent, parse fixed deprel (parent still good): GLD!PD!SYS+D
            # gold changed parent, parse fixed parent and deprel: GLD!PD!SYS+PD
            # gold changed parent, parse spoiled deprel (parent still good): GLD!PD!SYS-D
            # gold changed parent, parse spoiled parent (regardless deprel): GLD!PD!SYS-PD
            my $x = 'OTHER';
            if($gf1[6] == $gf2[6] && $gf1[7] eq $gf2[7])
            {
                if($f1[6] == $f2[6] && $f1[7] eq $f2[7])
                {
                    $x = 'NOCHANGE';
                }
                elsif($f1[6] == $gf1[6] && $f2[6] == $gf2[6])
                {
                    # We know that the parse changed and it was not the parent, so it must have been the deprel.
                    if($f1[7] ne $gf1[7] && $f2[7] eq $gf2[7])
                    {
                        $x = 'GLD=SYS+D';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                    elsif($f1[7] eq $gf1[7] && $f2[7] ne $gf2[7])
                    {
                        $x = 'GLD=SYS-D';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                    elsif($f1[7] ne $gf1[7] && $f2[7] ne $gf2[7])
                    {
                        $x = 'GLD=SYS=D0';
                        $x .= ':'.$f1[7].'>'.$f2[7].'(>'.$gf2[7].')' if($output eq 'deprel');
                    }
                }
                elsif($f1[6] != $gf1[6] && $f2[6] == $gf2[6])
                {
                    # The parent has been fixed. What about the deprel?
                    if($f1[7] ne $gf1[7] && $f2[7] eq $gf2[7])
                    {
                        $x = 'GLD=SYS+PD';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                    # The remaining possibilities:
                    # - The parent has been fixed, the deprel was already OK and stayed so (hence it did not change, because the gold deprel did not).
                    # - The parent has been fixed but the deprel is still wrong (changed or not).
                    # - The parent was fixed but the deprel was spoiled.
                    elsif($f1[7] eq $gf1[7] && $f2[7] eq $gf2[7])
                    {
                        $x = 'GLD=SYS+P1D';
                        $x .= ':'.$f2[7] if($output eq 'deprel');
                    }
                    else
                    {
                        $x = 'GLD=SYS+P';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                }
                elsif($f1[6] == $gf1[6] && $f2[6] != $gf2[6])
                {
                    # The parent has been spoiled. What about the deprel?
                    if($f1[7] eq $gf1[7] && $f2[7] ne $gf2[7])
                    {
                        $x = 'GLD=SYS-PD';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                    # The remaining possibilities:
                    # - The parent has been spoiled, the deprel was already OK and stayed so (hence it did not change, because the gold deprel did not).
                    # - The parent has been spoiled and the deprel is still wrong (changed or not).
                    # - The parent was spoiled but the deprel was fixed.
                    elsif($f1[7] eq $gf1[7] && $f2[7] eq $gf2[7])
                    {
                        $x = 'GLD=SYS-P1D';
                        $x .= ':'.$f2[7] if($output eq 'deprel');
                    }
                    else
                    {
                        $x = 'GLD=SYS-P';
                        $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                    }
                }
                elsif($f1[6] != $gf1[6] && $f2[6] != $gf2[6])
                {
                    $x = 'GLD=SYS=0';
                    # It probably does not make sense to report the deprels here.
                }
                else
                {
                    # This is a sanity check that we covered all possibilities
                    # above. We should not end up here.
                    $x = 'GLD=OTHER';
                }
            }
            # Gold deprel changed but the relation still connects the same two nodes.
            elsif($gf1[6] == $gf2[6] && $gf1[7] ne $gf2[7])
            {
                if($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] eq $gf1[7] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!D!SYS=1';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif(($f1[6] != $gf1[6] || $f1[7] ne $gf1[7]) && ($f2[6] != $gf2[6] || $f2[7] ne $gf2[7]))
                {
                    $x = 'GLD!D!SYS=0';
                }
                elsif($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] ne $gf1[7] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!D!SYS+D';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] != $gf1[6] && $f2[6] == $gf2[6] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!D!SYS+PD';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] eq $gf1[7] && $f2[7] ne $gf2[7])
                {
                    $x = 'GLD!D!SYS-D';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] == $gf1[6] && $f2[6] != $gf2[6])
                {
                    $x = 'GLD!D!SYS-PD';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                else
                {
                    # This is a sanity check that we covered all possibilities
                    # above. We should not end up here.
                    $x = 'GLD!D!OTHER';
                }
            }
            else # different parent, regardless deprel
            {
                if($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] eq $gf1[7] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!PD!SYS=1';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif(($f1[6] != $gf1[6] || $f1[7] ne $gf1[7]) && ($f2[6] != $gf2[6] || $f2[7] ne $gf2[7]))
                {
                    $x = 'GLD!PD!SYS=0';
                }
                elsif($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] ne $gf1[7] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!PD!SYS+D';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] != $gf1[6] && $f2[6] == $gf2[6] && $f2[7] eq $gf2[7])
                {
                    $x = 'GLD!PD!SYS+PD';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] == $gf1[6] && $f2[6] == $gf2[6] && $f1[7] eq $gf1[7] && $f2[7] ne $gf2[7])
                {
                    $x = 'GLD!PD!SYS-D';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                elsif($f1[6] == $gf1[6] && $f2[6] != $gf2[6])
                {
                    $x = 'GLD!PD!SYS-PD';
                    $x .= ':'.$f1[7].'>'.$f2[7] if($output eq 'deprel');
                }
                else
                {
                    # This is a sanity check that we covered all possibilities
                    # above. We should not end up here.
                    $x = 'GLD!PD!OTHER';
                }
            }
            # To reduce confusion, remove the SYS info from the tag if comparing the gold files.
            if($label =~ m/ gold /)
            {
                $x =~ s/SYS=1//;
            }
            $nt{$x}++;
            $totalnt{$x}++; # global hash
            # If required, print the CoNLL-U file with the comparison in MISC.
            if($output eq 'conllu')
            {
                my @misc = ();
                push(@misc, "Eval=$x");
                push(@misc, "Before=$f1[6]:$f1[7]");
                push(@misc, "After=$f2[6]:$f2[7]");
                push(@misc, "GoldBefore=$gf1[6]:$gf1[7]");
                push(@misc, "GoldAfter=$gf2[6]:$gf2[7]");
                $f2[9] = join('|', @misc);
                $f2[4] = '_'; # erase xpos
                $f2[5] = '_'; # erase feats
                print(join("\t", @f2), "\n");
            }
        }
        print("\n") if($output eq 'conllu');
    }
    if($output ne 'conllu')
    {
        #my $evaluation = join(', ', map {"$nt{$_} $_"} (sort(keys(%nt))));
        my $evaluation = join(', ', map {"$nt{$_} $_"} (sort {my $r = $nt{$b} <=> $nt{$a}; unless($r) {$r = $a cmp $b} $r} (keys(%nt))));
        print("SUMMARY $label compared $ns_compared/$ns1 sents: $evaluation\n");
    }
}



#------------------------------------------------------------------------------
# Reads a CoNLL-U file into memory. Returns an array of sentences.
#------------------------------------------------------------------------------
sub read_conllu
{
    my $filename = shift;
    my @doc = ();
    my @sentence = ();
    open(FILE, $filename) or die("Cannot read '$filename': $!");
    while(<FILE>)
    {
        if(m/^\s*$/)
        {
            push(@doc, [@sentence]);
            @sentence = ();
        }
        # Only store the regular node lines. We do not need anything else.
        elsif(m/^[0-9]+\t/)
        {
            chomp;
            push(@sentence, $_);
        }
    }
    close(FILE);
    return @doc;
}
