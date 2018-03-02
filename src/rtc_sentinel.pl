#!/usr/bin/perl

use FileHandle;
use File::Basename;
use Getopt::Long;
use File::Copy;
use File::Glob ':glob';
use Cwd;
use Env qw(GAMMA_HOME);

my $browse_res = 30;
my $res = 10.0;

if (($#ARGV + 1) < 1) {die <<EOS ;}

usage: $0 <options> output
	output		Output RTC file timedate string
	-e dem 		(option) specify a DEM file to use
        -o res          (option) specify the output resolution (default $res meters)
	-n		(option) do not perform matching
	-d		(option) if matching fails, use dead reckoning
        -g              (option) create gamma0 instead of sigma0 
	-l 		(option) only create a lo-res output (30m)

EOS

my $dem = '';
my $lo_flg = 0;
GetOptions ('e=s' => \$dem,'o=f' => \$res, 'n' => \$no_match_flg, 'd' => \$dead_flg, 'g' => \$gamma_flg, 'l' => \$lo_flg );

my $output = $ARGV[0];
my $log = "$output.log";
my $log_dir = cwd();
$log = $log_dir."/".$log;

print "===================================================================\n";
print "                      Sentinel RTC Program\n";
print "===================================================================\n";
if ($no_match_flg) { print "Turning off all matching\n";}
elsif ($dead_flg)  { print "If matching fails, use dead reckoning\n";}
if ($gamma_flg)    { print "Creating gamma0 output\n";}
if ($lo_flg)       { print "Creating low resolution (30m) ouput\n";  $res = 30.0;}
print "Processing resolution is $res meters\n";
print "\n";

# 
# Get the beam mode for this input file
#
my $mode = '';
$plat = "a";
$type = '';
my @list = glob "S1*.SAFE";
foreach my $file ( @list ) { 
  print "file is $file\n";
  $mode = substr($file,4,2); 
  $mode = lc($mode);
  $plat = substr($file,2,1);
  $type = substr($file,7,4);
  $date = substr($file,17,8);
  if ($type =~ /SLC/) { $type = "SLC"; }
  else {
    eval {
        execute("get_orb.py $file","$log")
    } or do {
        print "\nUnable to get precision orbit... continuing\n";
    }
  }
} 

if ($plat eq '') { die "Can't find a platform value\n"; }
else { print "Found Sentinel-1$plat\n"; }

$plat = lc($plat);

if ($mode eq '') { die "Can't find a sentinel file to process\n"; }
else { print "Found beam mode $mode\n"; }

#
# Get the DEM file that matches this scene
#
if ($dem eq '') {
  print "Getting a DEM file covering this SAR image\n";
  my @cc = get_cc();
  $min_lon = $cc[0];
  $max_lon = $cc[1];
  $min_lat = $cc[2];
  $max_lat = $cc[3];

  $dem = "big.dem";
  $parfile = "$dem.par";

  execute("get_dem.py -p 10 -u $min_lon $min_lat $max_lon $max_lat tmpdem.tif","$log");
  execute("utm2dem.py tmpdem.tif $dem $parfile","$log");

} elsif ($dem =~ /tif$/) {
  print "Using GeoTIFF DEM $dem\n";
  $tiff_dem = $dem;
  $dem = "big.dem";
  $parfile = "$dem.par";
  execute("utm2dem.py $tiff_dem $dem $parfile","$log");
} elsif (-e "$dem.par") {
  print "Using GAMMA DEM file $dem with parameter file $dem.par\n";
  $parfile = "$dem.par";
} else {
  die "Unrecognized DEM: $dem";
}  

#
# Start processing the scene
#
my $num_vv = 0;
my @vv = glob "*/*/*vv*.tiff";
foreach my $v ( @vv ) { ++$num_vv; }
if ($num_vv == 1 || $num_vv == 3) { 
  print "\nFound VV polarization - processing\n\n"; 
  $main_pol = "vv";
  $cross_pol = "vh";
  process_pol("$main_pol","$res","$no_match_flg","$dead_flg","$gamma_flg","$browse_res","$output","$mode","$type","$date","$log");

  my $num_vh = 0;
  my @vh = glob "*/*/*vh*.tiff";
  foreach my $v ( @vh ) { ++$num_vh; }
  if ($num_vh == 1 || $num_vh == 3) { 
    print "\nFound VH polarization - processing\n\n"; 
    $multi_pol = 1;
    process_2nd_pol("$cross_pol","$res","$gamma_flg","$browse_res","$output","$mode","$dem","$type","$date","$log");
  }
}

my $num_hh = 0;
my @hh = glob "*/*/*hh*.tiff";
foreach my $h ( @hh ) { ++$num_hh; }
if ($num_hh == 1 || $num_hh == 3) { 
  print "\nFound HH polarization - processing\n\n"; 
  $main_pol = "hh";
  $cross_pol = "hv";
  process_pol("$main_pol","$res","$no_match_flg","$dead_flg","$gamma_flg","$browse_res","$output","$mode","$type","$date","$log");

  my $num_hv = 0;
  my @hv = glob "*/*/*hv*.tiff";
  foreach my $h ( @hv ) { ++$num_hv; }
  if ($num_hv == 1 || $num_hv == 3) { 
    print "\nFound HV polarization - processing\n\n"; 
    $multi_pol = 1;
    process_2nd_pol("$cross_pol","$res","$gamma_flg","$browse_res","$output","$mode","$dem","$type","$date","$log");
  }
}

if ($num_hh == 0 && $num_vv == 0) {die "ERROR: No vv or hh pol found\n";}

#
# Create geo-browse and kmz
#
if ($res > 10.0) { $outname = "s1$plat-$mode-rtcm-$output"; }
else { $outname = "s1$plat-$mode-rtch-$output"; }

if ($multi_pol==1) {
  execute("rtc2color.py -cleanup geo_${main_pol}/${output}_${main_pol}_${browse_res}m.tif geo_${cross_pol}/${output}_${cross_pol}_${browse_res}m.tif -24 ${output}_hires.tif",$log);
  my $outdir = "PRODUCT";
  execute("makeAsfBrowse.py ${output}_hires.tif ${outdir}/${outname}",$log);
} else {
  chdir("geo_${main_pol}");
  if ($res >= $browse_res) {
    copy("tc_${main_pol}.img","${output}_${main_pol}_${browse_res}m.img") or die ("ERROR $0: Copy failed: $!");
    copy("tc_${main_pol}.meta","${output}_${main_pol}_${browse_res}m.meta") or die ("ERROR $0: Copy failed: $!");
  } else {
    execute("asf_import -format geotiff ${output}_${main_pol}_${browse_res}m.tif ${output}_${main_pol}_${browse_res}m",$log);
  }
  execute("sqrt_img ${output}_${main_pol}_${browse_res}m ${output}_amp_${browse_res}m",$log);
  execute("asf_export -format geotiff -byte sigma ${output}_amp_${browse_res}m ${output}.amp.tif",$log);
  my $outdir = "../PRODUCT";
  execute("makeAsfBrowse.py ${output}.amp.tif ${outdir}/${outname}",$log);
  chdir("..");
}

if ($res > 10.0) {
  $hdf5_list_name = "hdf5_list_rtcm.txt";
  $outname = "s1$plat-$mode-rtcm-$output";
  $outfile = "s1$plat-$mode-rtcm-$main_pol-$output";
} else { 
  $hdf5_list_name = "hdf5_list_rtch.txt";
  $outname = "s1$plat-$mode-rtch-$output";
  $outfile = "s1$plat-$mode-rtch-$main_pol-$output";
} 

generate_xml($hdf5_list_name,$outname,$main_pol,$outfile,$multi_pol,$cross_pol,$output,$log,$dem_type, $type);

#Create consolidated log file
$out = "PRODUCT";
$new_basename = "s1$plat-$mode-rtcm-$output";
print("Creating log file: $out/$new_basename.log\n");
$logname = "$out/$new_basename.log";
open (LOG, ">$logname") or died("ERROR: Could not open consolidated log file: $logname: $!");
print LOG "Consolidated log for: $output\n";
my $options_string = "";

$options_string .= "-l " if $lo_flg;
$options_string .= "-d " if $dead_flg;
$options_string .= "-n " if $no_match_flg;
$options_string .= "-g " if $gamma_flg;

print LOG "$0 options: $options_string\n\n";
print LOG "$out_str\nDone!!!\n\n";
close(LOG);
add_log($log, $logname);


#Add RTC log files
if ($num_vv == 1) { $dir = "geo_vv";}
else {$dir = "geo_hh";}

add_log("$dir/mk_geo_radcal_0.log", $logname);
add_log("$dir/mk_geo_radcal_1.log", $logname);
add_log("$dir/mk_geo_radcal_2.log", $logname);
add_log("$dir/mk_geo_radcal_3.log", $logname);
add_log("coreg_check.log", $logname);

print "\nDone!!!\n\n";
exit;

#
# Generate XML files
#
sub generate_xml() {
  my ($hdf5_list_name,$outname,$main_pol,$outfile,$multi_pol,$cross_pol,$output,$log,$dem_type,$type) = @_;

  # Create necessary meta file
  my @list = glob "S1*.SAFE";
  for (@list) {
 	$path = $_;
  }

  print "found path $path\n";

  $etc_dir = dirname($0) . "/../etc";
  copy("$etc_dir/sentinel_xml.xsl","sentinel_xml.xsl") or die ("ERROR $0: Copy failed: $!");

  $out = "PRODUCT";

  $cmd = "xsltproc --stringparam path $path --stringparam timestamp timestring --stringparam file_size 1000 --stringparam server stuff --output out.xml sentinel_xml.xsl $path/manifest.safe";
  execute($cmd,$log);

  if ($type =~ /GRD/) {

      $cmd = "xml2meta.py sentinel out.xml out.meta";
      execute($cmd,$log);

      $version_file = "$etc_dir/version.txt";
      $gap_rtc_version = "";
      if (open(VER, "$version_file")) {
        $gap_rtc_version = <VER>;
        chomp($gap_rtc_version);
      } else {
        print "No version.txt file found in $etc_dir\n";
      }

      $version_file = "$GAMMA_HOME/ASF_Gamma_version.txt";
      $gamma_version = "20150702";
      if (open(VER, "$version_file")) {
        $gamma_version = <VER>;
        chomp($gamma_version);
      } else {
        print "No ASF_Gamma_version.txt file found in $GAMMA_HOME\n";
      }

      open(HDF5_LIST,"> $hdf5_list_name") or die("ERROR $0: cannot create $hdf5_list_name\n\n");
      print HDF5_LIST "[GAMMA RTC]\n";
      print HDF5_LIST "granule = $outname\n";
      print HDF5_LIST "metadata = out.meta\n"; 

      $geo_dir = "geo_$main_pol"; 
      $dem_seg = "geo_${main_pol}/area.dem";
      $dem_seg_par = "geo_${main_pol}/area.dem_par";
     
      print HDF5_LIST "oversampled dem file = $dem_seg\n";
      print HDF5_LIST "oversampled dem metadata = $dem_seg_par\n";
      print HDF5_LIST "original dem file = $out/$outname-dem.tif\n";
      print HDF5_LIST "layover shadow mask = $out/$outname-ls_map.tif\n";
      print HDF5_LIST "layover shadow stats = $geo_dir/ls_map.stat\n";
      print HDF5_LIST "incidence angle file = $out/$outname-inc_map.tif\n";
      print HDF5_LIST "incidence angle metadata = $geo_dir/inc_map.meta\n";

      print HDF5_LIST "input $main_pol file = $outfile\n";
      print HDF5_LIST "terrain corrected $main_pol metadata = $geo_dir/tc_$main_pol.meta\n";
      print HDF5_LIST "terrain corrected $main_pol file = $out/$outfile.tif\n";

      if ($multi_pol==1) {
        $outfile2 = $outfile;
        $outfile2 =~ s/$main_pol/$cross_pol/;
        print HDF5_LIST "input $cross_pol file = $outfile2\n";
        $geo_dir2 = $geo_dir;
        $geo_dir2 =~ s/$main_pol/$cross_pol/;
        print HDF5_LIST "terrain corrected $cross_pol metadata = $geo_dir2/tc_$cross_pol.meta\n";
        print HDF5_LIST "terrain corrected $cross_pol file = $out/$outfile2.tif\n";
      }

      print HDF5_LIST "initial processing log = $output.log\n";
      print HDF5_LIST "terrain correction log = $output.log\n";
      print HDF5_LIST "main log = $log\n";
      print HDF5_LIST "mk_geo_radcal_0 log = geo_$main_pol/mk_geo_radcal_0.log\n";
      print HDF5_LIST "mk_geo_radcal_1 log = geo_$main_pol/mk_geo_radcal_1.log\n";
      print HDF5_LIST "mk_geo_radcal_2 log = geo_$main_pol/mk_geo_radcal_2.log\n";
      print HDF5_LIST "mk_geo_radcal_3 log = geo_$main_pol/mk_geo_radcal_3.log\n";
      print HDF5_LIST "coreg_check log = coreg_check.log\n";
      print HDF5_LIST "mli.par file = ${output}.${main_pol}.mgrd.par\n";
      print HDF5_LIST "gamma version = $gamma_version\n";
      print HDF5_LIST "gap_rtc version = $gap_rtc_version\n";
      print HDF5_LIST "dem source = $dem_type\n";
      print HDF5_LIST "browse image = $out/$outname.png\n";
      print HDF5_LIST "kml overlay = $out/$outname.kmz\n";
      close(HDF5_LIST);

      execute("write_hdf5_xml $hdf5_list_name $outname.xml",$log);

      # We can't use execute for xsltproc because of the redirect
      print "Generating $granule.iso.xml with $etc_dir/rtc_iso.xsl\n";
      $exit = system("xsltproc $etc_dir/rtc_iso.xsl $outname.xml >$outname.iso.xml");
      $exit == 0 or die("ERROR $0: non-zero exit status for xsltproc");

      copy("$outname.iso.xml","$out/$outname.iso.xml") or die ("ERROR $0: Copy failed: $!");
      
  } else {
      copy("out.xml","$out/$outname.xml") or die ("ERROR $0: Copy failed: $!");
  }
}

#
# terrain geocode the cross-pol channel using the refinement information from the main channel
# thus bypassing modes 0, 1, and 2 of mk_geo_radcal
# creates the main cross-pol tif file
#
sub process_2nd_pol() {
  my ($pol2,$res,$gamma_flg,$browse_res,$output,$mode,$dem,$type,$date,$log) = @_;
  if ($pol2 eq "hv") { $pol1 = "hh"; }
  else { $pol1 = "vv"; }

  my $options = "-p -j -n 6 -q -c ";
  $options .= "-g " if $gamma_flg;
  print "Cross-pol is $pol2; Main pol is $pol1\n";

  if ($type =~ /GRD/) {
    print "Ingesting GRD file into Gamma format\n";
    $cmd = "par_S1_GRD */*/*$pol2*.tiff */*/*$pol2*.xml */*/*/calibration-*$pol2*.xml */*/*/noise-*$pol2*.xml $output.$pol2.GRD.par $output.$pol2.GRD";
    execute($cmd,$log);

    eval {
      execute("S1_OPOD_vec $output.$pol2.GRD.par *.EOF",$log);
    } or do {
      print "\nUnable to get precision orbit... continuing\n";
    };

    $look_fact = int ($res/10+0.5);
    if ($look_fact > 1) {
      print "Multi-looking GRD file\n";
      $cmd = "multi_look_MLI $output.$pol2.GRD $output.$pol2.GRD.par $output.$pol2.mgrd $output.$pol2.mgrd.par $look_fact $look_fact";
      execute($cmd,$log);
    } else {
      copy("$output.$pol2.GRD","$output.$pol2.mgrd") or die ("ERROR $0: Copy failed: $!");
      copy("$output.$pol2.GRD.par","$output.$pol2.mgrd.par") or die ("ERROR $0: Copy failed: $!");
    }
  } else {
    print "Ingesting SLC file into Gamma format\n";
    $cmd = "par_s1_slc.py $pol2";
    execute($cmd,$log);

    $workDir = cwd();
    chdir($date);
    $cmd = "SLC_copy_S1_fullSW.py ${workDir}/DATA $date slc.tab burst.tab 2";
    execute($cmd,$log);

    chdir("../DATA");
    copy("${date}.mli","../$output.$pol2.mgrd") or die ("ERROR $0: Copy failed: $!");
    copy("${date}.mli.par","../$output.$pol2.mgrd.par") or die ("ERROR $0: Copy failed: $!");
    chdir("..");
  }   

  $geo_dir = "geo_$pol2";
  $gc0 = "$geo_dir/image_0.map_to_rdc";
  $ls_map = "$geo_dir/image_0.ls_map";
  $inc_map = "$geo_dir/image_0.inc_map";
  $sim_map = "$geo_dir/image_0.sim";
  $pix_map = "$geo_dir/image_0.pix_map";
  $diff_par = "$geo_dir/image.diff_par";

  $gc0_main = $gc0;
  $gc0_main =~ s/$pol2/$pol1/g;

  $ls_map_main = $ls_map;
  $ls_map_main =~ s/$pol2/$pol1/g;

  $pix_map_main = $pix_map;
  $pix_map_main =~ s/$pol2/$pol1/g;

  $sim_map_main = $sim_map;
  $sim_map_main =~ s/$pol2/$pol1/g;

  $inc_map_main = $inc_map;
  $inc_map_main =~ s/$pol2/$pol1/g;

  $diff_par_main = $diff_par;
  $diff_par_main =~ s/$pol2/$pol1/g;

  unless (-d $geo_dir){
    print "creating directory for output geocoded image products: $geo_dir\n";
    $exit = system("mkdir $geo_dir");
    $exit == 0 or die "ERROR $0: non-zero exit status: mkdir $geo_dir\n";
  }

  print "Copying diff par file $diff_par_main to $diff_par\n";

  copy("$diff_par_main","$diff_par") or die ("ERROR $0: Copy failed: $!");

  execute("ln -f $gc0_main $gc0",$log);
  execute("ln -f $ls_map_main $ls_map",$log);
  execute("ln -f $inc_map_main $inc_map",$log);
  execute("ln -f $sim_map_main $sim_map",$log);
  execute("ln -f $pix_map_main $pix_map",$log);

  $cmd = "mk_geo_radcal $output.$pol2.mgrd $output.$pol2.mgrd.par $dem $dem.par geo_$pol1/area.dem geo_$pol1/area.dem_par $geo_dir image $res 3 $options";
  execute($cmd,$log);

  chdir("$geo_dir");

  execute("asf_import -format geotiff image_cal_map.mli.tif tc_$pol2",$log);
  execute("stats -nostat -overmeta -mask 0 tc_$pol2",$log);

  if ($res >= $browse_res) {
    copy("image_cal_map.mli.tif","${output}_${pol2}_${browse_res}m.tif") or die ("ERROR $0: Copy failed: $!");
  } else {  
    execute("resample -square $browse_res tc_$pol2 ${output}_${pol2}_${browse_res}m",$log);
    fix_band_name("${output}_${pol2}_${browse_res}m.meta",$pol);
    execute("asf_export -format geotiff ${output}_${pol2}_${browse_res}m ${output}_${pol2}_${browse_res}m.tif",$log);
  }

  if ($res > 10.0) { $outname = "s1$plat-$mode-rtcm-$pol2-$output.tif"; }
  else { $outname = "s1$plat-$mode-rtch-$pol2-$output.tif"; }
  my $out = "../PRODUCT";
  move("image_cal_map.mli.tif","$out/$outname") or die "Move failed: image_cal_map.mli.tif -> ../$outname";

  chdir("..");

}

#
# Main routine to process a single pol of data
# Creates the main .tif file, the dem, ls_map, and inc_map
#
sub process_pol() {
  my ($pol,$res,$no_match_flg,$dead_flg,$gamma_flg,$browse_res,$output,$mode,$type,$date,$log) = @_;

  if ($type =~ "GRD") {  
    print "Ingesting GRD file into Gamma format\n";
    $cmd = "par_S1_GRD */*/*$pol*.tiff */*/*$pol*.xml */*/*/calibration-*$pol*.xml */*/*/noise-*$pol*.xml $output.$pol.GRD.par $output.$pol.GRD";
    execute($cmd,$log);
    
    eval {
      execute("S1_OPOD_vec $output.$pol.GRD.par *.EOF",$log);
    } or do {
      print "\nUnable to get precision orbit... continuing\n";
    };

    $look_fact = int ($res/10+0.5);
    if ($look_fact > 1) {
      print "Multi-looking GRD file\n";
      $cmd = "multi_look_MLI $output.$pol.GRD $output.$pol.GRD.par $output.$pol.mgrd $output.$pol.mgrd.par $look_fact $look_fact";
      execute($cmd,$log);
    } else {
      copy("$output.$pol.GRD","$output.$pol.mgrd") or die ("ERROR $0: Copy failed: $!");
      copy("$output.$pol.GRD.par","$output.$pol.mgrd.par") or die ("ERROR $0: Copy failed: $!");
    }   
  } else {
    print "Ingesting SLC file into Gamma format\n";
    $cmd = "par_s1_slc.py $pol";
    execute($cmd,$log);

    chdir($date); 
    my @slc_files = glob("*.slc");   
    my @slc_sort = sort @slc_files;
    my @par_files = glob("*.slc.par");   
    my @par_sort = sort @par_files;
    my @tops_files = glob("*.tops_par");   
    my @tops_sort = sort @tops_files;
    my $filename = 'slc.tab';
    open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
    print $fh "$slc_sort[0] $par_sort[0] $tops_sort[0]\n";
    print $fh "$slc_sort[1] $par_sort[1] $tops_sort[1]\n";
    print $fh "$slc_sort[2] $par_sort[2] $tops_sort[2]\n";
    close $fh;
    chdir("..");

    my @list = glob "S1*.SAFE";
    foreach my $file ( @list ) { 
        my $filename = 'burst.tab';
        open(my $fh, '>', $filename) or die "Could not open file '$filename' $!";
        $back = cwd();
        chdir($file);
        chdir("annotation");
        my @list2 = glob "*$pol*.xml";
        my @sort_list2 = sort @list2; 
        foreach my $file2 ( @sort_list2 ) {
            $lines_output = `cat $file2`;
            my @lines = split /\n/, $lines_output; #split into lines
            foreach my $line ( @lines ) {
                if ($line =~ m/\s+<burstList count="(\S+)">/) {
                    $burst_count = $1;
                }
            }
            print $fh "1 $burst_count\n";
        }
        close $fh;
        chdir($back);
        move("burst.tab","$date/burst.tab") or die "ERROR $0: Move failed: $!";
    }
    mkdir("DATA");
    $workDir = cwd();

    chdir($date);
    $cmd = "SLC_copy_S1_fullSW.py ${workDir}/DATA $date slc.tab burst.tab 2";
    execute($cmd,$log);

    chdir("../DATA");
    copy("${date}.mli","../$output.$pol.mgrd") or die ("ERROR $0: Copy failed: $!");
    copy("${date}.mli.par","../$output.$pol.mgrd.par") or die ("ERROR $0: Copy failed: $!");

    chdir("..");
  }
  my $options = "-p -j -n 6 -q -c ";
  $options .= "-g " if $gamma_flg;

  print "Running RTC process... initializing\n";
  $cmd = "mk_geo_radcal $output.$pol.mgrd $output.$pol.mgrd.par $dem $dem.par geo_$pol/area.dem geo_$pol/area.dem_par geo_$pol image $res 0 $options";
  execute($cmd,$log);
 
  if ($no_match_flg != 1) {
    print "Running RTC process... coarse matching\n";
    $cmd = "mk_geo_radcal $output.$pol.mgrd $output.$pol.mgrd.par $dem $dem.par geo_$pol/area.dem geo_$pol/area.dem_par geo_$pol image $res 1 $options";

    eval {
      execute($cmd,$log);
    } or do {
      print "$0: Determination of the initial offset failed, skipping initial offset\n";
    };

    print "Running RTC process... fine matching\n";
    $cmd = "mk_geo_radcal $output.$pol.mgrd $output.$pol.mgrd.par $dem $dem.par geo_$pol/area.dem geo_$pol/area.dem_par geo_$pol image $res 2 $options";

    eval {
      execute($cmd,$log);
    } or do {
      print "WARNING: Failed to determine offset model\n";
      if ($dead_flg != 1) { exit -1;}
      else {
        $diff_par = "geo_$pol/image.diff_par";
        print "WARNING: Coregistration has failed; defaulting to dead reckoning\n";
        execute("rm $diff_par",$log);
        $fail = 1;
      }
    };
    if ($fail != 1) {
      eval {
	my $offset = 250;
  	my $error = 4;
        execute("check_coreg.pl $res -o $offset -e $error $output",$log);
      } or do {
         print "WARNING: Failed coregistration check\n";
         if ($dead_flg != 1) {exit -1;}
         else {
           $diff_par = "geo_$pol/image.diff_par";
           print "WARNING: Coregistration has failed; defaulting to dead reckoning\n";
           execute("rm $diff_par",$log);
         }
      };
    }
  }

  print "Running RTC process... finalizing\n";
  $cmd = "mk_geo_radcal $output.$pol.mgrd $output.$pol.mgrd.par $dem $dem.par geo_$pol/area.dem geo_$pol/area.dem_par geo_$pol image $res 3 $options";
  execute($cmd,$log);

  chdir("geo_$pol");
  execute("data2geotiff area.dem_par image_0.ls_map 5 ${output}.ls_map.tif",$log);
  execute("data2geotiff area.dem_par image_0.inc_map 2 ${output}.inc_map.tif",$log);
  execute("data2geotiff area.dem_par area.dem 2 outdem.tif",$log);
  execute("gdal_translate -ot Int16 outdem.tif ${output}.dem.tif",$log);
  execute("asf_import -format geotiff ${output}.ls_map.tif ls_map",$log);
  execute("stats -overstat -overmeta ls_map",$log);
  execute("asf_import -format geotiff ${output}.inc_map.tif inc_map",$log);
  execute("stats -overstat -overmeta -mask 0 inc_map",$log);
  execute("asf_import -format geotiff image_cal_map.mli.tif tc_$pol",$log);
  execute("stats -nostat -overmeta -mask 0 tc_$pol",$log);

  if ($res >= $browse_res) {
    copy("image_cal_map.mli.tif","${output}_${pol}_${browse_res}m.tif")  or die ("ERROR $0: Copy failed: $!");
  } else {  
    execute("resample -square $browse_res tc_$pol ${output}_${pol}_${browse_res}m",$log);
    fix_band_name("${output}_${pol}_${browse_res}m.meta",$pol);
    execute("asf_export -format geotiff ${output}_${pol}_${browse_res}m ${output}_${pol}_${browse_res}m.tif",$log);
  }

  my $out = "../PRODUCT";
  mkdir($out);

  if ($res > 10.0) { $outname = "s1$plat-$mode-rtcm-$pol-$output"; }
  else { $outname = "s1$plat-$mode-rtch-$pol-$output"; }

  move("image_cal_map.mli.tif","$out/$outname.tif") or die "Move failed: image_cal_map.mli.tif -> $out/$outname.tif";

  if ($res > 10.0) { $outname = "s1$plat-$mode-rtcm-$output"; }
  else { $outname = "s1$plat-$mode-rtch-$output"; }

  move("${output}.ls_map.tif","$out/${outname}-ls_map.tif") or die "ERROR $0: Move failed: $!";
  move("${output}.inc_map.tif","$out/${outname}-inc_map.tif") or die "ERROR $0: Move failed: $!";
  move("${output}.dem.tif","$out/${outname}-dem.tif") or die "ERROR $0: Move failed: $!";

  chdir("..");
}


#
# Extract the corner coordinates from the annotation xml file
#
sub get_cc {

    my $annotation = `cat */*/s1$plat*.xml`;
    my @ann = split /\n/, $annotation;   # split into lines

    my $min_lat = 90;
    my $min_lon = 180;
    my $max_lat = -90;
    my $max_lon = -180; 

    foreach my $line (@ann) {
      if ($line =~ m/<latitude>(\S+)<\/latitude>/) {
        $max_lat = ($1 > $max_lat) ? $1 : $max_lat;
        $min_lat = ($1 < $min_lat) ? $1 : $min_lat;
      }
      if ($line =~ m/<longitude>(\S+)<\/longitude/) {
        $max_lon = ($1 > $max_lon) ? $1 : $max_lon;
        $min_lon = ($1 < $min_lon) ? $1 : $min_lon;
      }
    } 

    $dmax_lat = sprintf("%.8g",$max_lat);
    $dmin_lat = sprintf("%.8g",$min_lat);
    $dmax_lon = sprintf("%.8g",$max_lon);
    $dmin_lon = sprintf("%.8g",$min_lon);

    $dmax_lat = $dmax_lat + 0.15;
    $dmin_lat = $dmin_lat - 0.15;
    $dmax_lon = $dmax_lon + 0.15;
    $dmin_lon = $dmin_lon - 0.15;

    print "    found max latitude of $dmax_lat\n";
    print "    found min latitude of $dmin_lat\n";
    print "    found max longitude of $dmax_lon\n";
    print "    found min longitude of $dmin_lon\n";

    @parms = ("$dmin_lon","$dmax_lon","$dmin_lat","$dmax_lat");
    return @parms;
}

sub execute{
  my ($command, $log) = @_;
  if (-e $log){open(LOG,">>$log") or die "\nERROR $0: cannot open log file: $log\n";}
  else {open(LOG,">$log") or die "\nERROR $0: cannot open log file: $log\n";}
  print "$command\n";
  print LOG ("\n${command}\n");
  my $out = `$command`;
  if ($out =~ /ERROR: Unable to find a DEM/) {
    die "ERROR: Unable to find a DEM";
  }
  my $exit = $? >> 8;
  print ("\nsentinel_rtc.pl is Running: ${command}\nOutput:\n${out}\n----------\n");
  print LOG ("\n${out}\n");
  close LOG;
  $exit == 0 or die "ERROR $0: non-zero exit status: $command\n"
}

#
# Fix the band name in an ASF internal meta file 
# by setting the band name equal to the polarization
#
sub fix_band_name {
  my ($metafile,$pol) = @_;
  $meta_output = `cat $metafile`;
  my @meta = split /\n/, $meta_output; #split into lines
  open(DPAR,"> tmp.meta") or die("ERROR $0: Cant create tmp meta file\n\n");
  foreach my $line (@meta){
    if ($line =~ m/bands:/) {
      print DPAR "    bands: $pol\n";
    } else {
      print DPAR "$line\n";
    }
  }
  close(DPAR);
  move("tmp.meta",$metafile) or die("ERROR $0: Move failed: $!");
}

sub add_log {
  my ($log, $full_log) = @_;

  open(FL,">>$full_log") or died("ERROR: Could not open $full_log: $!");
  print FL "=======================================\n";
  print FL "Log: $log\n";
  print FL "=======================================\n";
  if (!open(LG,"$log")) {
    print FL "(not found)\n\n";
    close(FL);
    return;
  }

  foreach my $logline (<LG>) {
    print FL "$logline";
  }
  close(LG);

  print FL "\n";
  close(FL);
}

