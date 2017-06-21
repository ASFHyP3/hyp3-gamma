#!/usr/bin/perl
use FileHandle;
use File::Basename;
use Getopt::Long;
use File::Copy;

if (($#ARGV + 1) < 2){die <<EOS ;}
*** $0

usage: $0 [options] <post> <SARFILE> 
    <post>    (input)  Posting of the SAR image
    SARFILE   (input)  Input SAR file to process 
    -m <num matches>   Set the number of matches to use (depricated)
    -o <max offset>    Set the maximum allowable offset (meters)
    -e <max error>     Set the maximum allowable standard deviation of offset fit (pixels)

EOS

GetOptions ('m=i' => \$matches_flg,'o=i' => \$offset_flg,'e=f' => \$error_flg );


$post = $ARGV[0];
$arg = $ARGV[1];
($sarfile,$path) = fileparse($arg);

$min_matches = 50;
$max_offset = 50;
$max_error = 2;

print "Checking coregistration for $sarfile using $post meters\n";
 
if ($matches_flg != 0) {
  print "Setting minimum number of matches to $matches_flg\n";
  $min_matches = $matches_flg;
}

if ($offset_flg != 0) {
  print "Setting maximum offset to be $offset_flg\n";
  $max_offset = $offset_flg;
}

if ($error_flg != 0) {
  print "Setting maximum error to be $error_flg\n";
  $max_error = $error_flg;
}

open(LOG,">>coreg_check.log") or die "\nERROR $0: cannot open log file: coreg_check.log\n";
print LOG "SAR file: $sarfile\n";
if ($matches_flg != 0) { print LOG "Checking for $min_matches matches, $max_offset offset, and $max_error errors\n";}
else { print LOG "Checking for $max_offset meter offset and $max_error errors (std dev of fit)\n";}

if (-e "geo_HH/mk_geo_radcal_2.log") { $log = "geo_HH/mk_geo_radcal_2.log"; }
elsif (-e "geo_hh/mk_geo_radcal_2.log") { $log = "geo_hh/mk_geo_radcal_2.log"; }
elsif (-e "geo_vv/mk_geo_radcal_2.log") { $log = "geo_vv/mk_geo_radcal_2.log"; }
elsif (-e "geo/mk_geo_radcal_2.log") { $log = "geo/mk_geo_radcal_2.log"; }
else { die "ERROR $0: Can't find mk_geo_radcal_2.log file\n"; }

if  (-e $log) {
  open(TLOG,$log) or die "ERROR $0: could not open log: $log: $!\n\n";
  my (@lines) = <TLOG>;
  close(TLOG);

  while (my $line = shift(@lines)) {
 
    #
    # Only checks the number of matches if a values was passed on the command line
    #
    if ($matches_flg != 0) {  
      if ($line =~ /final solution:\s+(\S+)/) {
        $matches = $1;
        print LOG "Number of matches is $matches\n";
        if ($matches < $min_matches) {
          print LOG "WARNING: not enough matches, using dead reckoning\n";
          print LOG "Granule failed coregistration\n";
          $ret = -1;
          close LOG;
          exit $ret;
        } 
      }
    }
 
    if ($line =~ /final range offset poly. coeff.:\s+(\S+)/) {
      $r1 = $1;
      $r2 = 0;
      $r3 = 0;
      $r4 = 0;
      $r5 = 0;
      $r6 = 0;
      print LOG "Range offset is $r1\n";
    }

    if ($line =~ /final range offset poly. coeff.:\s+(\S+)\s+(\S+)\s+(\S+)/) {
      $r1 = $1;
      $r2 = $2;
      $r3 = $3;
      $r4 = 0;
      $r5 = 0;
      $r6 = 0;
      print LOG "Range polynomial is $r1 $r2 $r3\n";
    }

    if ($line =~ /final range offset poly. coeff.:\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)/) {
      $r1 = $1;
      $r2 = $2;
      $r3 = $3;
      $r4 = $4;
      $r5 = $5;
      $r6 = $6;
      print LOG "Range polynomial is $r1 $r2 $r3 $r4 $r5 $r6\n";
    }

    if ($line =~ /final azimuth offset poly. coeff.:\s+(\S+)/) {
      $a1 = $1;
      $a2 = 0;
      $a3 = 0;
      $a4 = 0;
      $a5 = 0; 
      $a6 = 0;
      print LOG "Azimuth offset is $a1\n";
    }

    if ($line =~ /final azimuth offset poly. coeff.:\s+(\S+)\s+(\S+)\s+(\S+)/) {
      $a1 = $1;
      $a2 = $2;
      $a3 = $3;
      $a4 = 0;
      $a5 = 0; 
      $a6 = 0;
      print LOG "Azimuth polynomial is $a1 $a2 $a3\n";
    }
 
    if ($line =~ /final azimuth offset poly. coeff.:\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)\s+(\S+)/) {
      $a1 = $1;
      $a2 = $2;
      $a3 = $3;
      $a4 = $4; 
      $a5 = $5; 
      $a6 = $6;
      print LOG "Azimuth polynomial is $a1 $a2 $a3 $a4 $a5 $a6\n";
    }
 
    if ($line =~ /final model fit std. dev. \(samples\) range:\s+(\S+)\s+\S+\s+(\S+)/) {
      $rn_error = $1;
      $az_error = $2;
      print LOG "Range std dev: $rn_error  Azimuth std dev: $az_error\n";
      $error = sqrt($rn_error * $rn_error + $az_error * $az_error);
      if ($error > $max_error) {
        print LOG "WARNING: std dev is too high, using dead reckoning\n";
        print LOG "Granule failed coregistration\n";
        $ret = -1;
        close LOG;
        exit $ret; 
      }
    }
  }
}

$log = glob('geo_??/*.diff_par');
if (-e $log) { $platform = "NOT_LEGACY"; }
else {
  $log = glob('geo/*.diff_par');
  if (-e $log) { $platform = "LEGACY"; }
  else { die "ERROR $0: Can't find diff_par file\n"; }
}

if (-e $log) {
  open(TLOG,$log) or die "ERROR $0: could not open log: $log: $!\n\n";
  my (@lines) = <TLOG>;
  close(TLOG);

  while (my $line = shift(@lines)) {
    if ($line =~ /range_samp_1:\s+(\S+)/) {
      $ns = $1;
      print LOG "Number of samples is $ns\n";
    }
    if ($line =~ /az_samp_1:\s+(\S+)/) {
      $nl = $1;
      print LOG "Number of lines is $nl\n";
    }
  }
} else { die "ERROR $0: Can't find diff par file $log\n"; }


# Point1 = 1, 1 
($rpt1,$apt1)=calc(1,1);
$pt1 = sqrt($rpt1*$rpt1 + $apt1*$apt1);
print LOG "Point 1 offset is $pt1\n";

# Point2 = ns, 1
($rpt2,$apt2) = calc($ns,1);
$pt2 = sqrt($rpt2*$rpt2 + $apt2*$apt2);
print LOG "Point 2 offset is $pt2\n";

# Point3 = 1, nl
($rpt3,$apt3) = calc(1,$nl);
$pt3 = sqrt($rpt3*$rpt3 + $apt3*$apt3);
print LOG "Point 3 offset is $pt3\n";

# Point4 = ns, nl
($rpt4,$apt4) = calc($ns,$nl);
$pt4 = sqrt($rpt4*$rpt4 + $apt4*$apt4);
print LOG "Point 4 offset is $pt4\n";

$top = max($pt1, $pt2, $pt3, $pt4);
print LOG "Biggest offset is $top pixels\n";

$offset = $top * $post;
print LOG "Found absolute offset of $offset meters\n";
if ($offset < $max_offset) {
  print LOG "...keeping offset\n";
  $ret = 0;
} else {
  print LOG "WARNING: offset too large, using dead reckoning\n";
  $ret = -1;
}

if ($ret == 0) { print LOG "Granule passed coregistration\n"; }
else { print LOG "Granule failed coregistration\n"; }

close LOG;

exit $ret;

sub max {
    my ($max, @vars) = @_;
    for (@vars) {
        $max = $_ if $_ > $max;
    }
    return $max;
}

sub calc {
    my ($s,$l) = @_;
    
    $rpt1 = $r1 + $r2 * $s + $r3 * $l + $r4*$s*$l + $r5*$s*$s + $r6*$l*$l;
    $apt1 = $a1 + $a2 * $s + $a3 * $l + $a4*$s*$l + $a5*$s*$s + $a6*$l*$l;

    return ($rpt1,$apt1)
}

