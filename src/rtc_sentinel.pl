#!/usr/bin/perl

use FileHandle;
use File::Basename;
use Getopt::Long;
use File::Copy;
use File::Glob ':glob';
use Cwd;
use Env qw(GAMMA_HOME);

my $kmz_res = 30;
my $res = 10.0;

if (($#ARGV + 1) < 1) {die <<EOS ;}

usage: $0 <options> output
	output		Output RTC file timedate string
	-e dem 		(option) specify a DEM file to use (DANGEROUS OPTION)
        -o res          (option) specify the output resolution (default $res meters)
	-n		(option) do not perform matching
	-d		(option) if matching fails, use dead reckoning
        -g              (option) create gamma0 instead of sigma0 
	-h              (option) create hi-res KMZ file ($kmz_res meters)
	-l 		(option) only create a lo-res output, don't upsample

EOS

my $dem = '';
my $lo_flg = 0;
GetOptions ('e=s' => \$dem,'o=f' => \$res, 'n' => \$no_match_flg, 'd' => \$dead_flg, 'g' => \$gamma_flg, 'h' => \$kmz_flg, 'l' => \$lo_flg );

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
if ($kmz_flg)      { print "Creating high resolution kmz file at $kmz_res meters\n";}
if ($lo_flg)       { print "Creating low resolution (30m) ouput\n";  $res = 30.0;}
print "Processing resolution is $res meters\n";
print "\n";

# 
# Get the beam mode for this input file
#
my $mode = '';
$plat = "a";
my @list = glob "S1*.SAFE";
foreach my $file ( @list ) { 
  print "file is $file\n";
  $mode = substr($file,4,2); 
  $mode = lc($mode);
  $plat = substr($file,2,1);
  eval {
      execute("get_orb.py $file","$log")
  } or do {
      print "\nUnable to get precision orbit... continuing\n";
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
  execute("utm2dem.pl tmpdem.tif $dem $parfile","$log");

} elsif ($dem =~ /tif$/) {
  print "Using GeoTIFF DEM $dem\n";

  $tiff_dem = $dem;
  $dem = "big.dem";
  $parfile = "$dem.par";

  execute("utm2dem.pl $tiff_dem $dem $parfile","$log");
} elsif (-e "$dem.par") {
  print "Using GAMMA DEM file $dem with parameter file $dem.par\n";
  $parfile = "$dem.par";
} else {
  die "Unrecognized DEM: $dem";
}  

#
# Set processing flow based upon DEM type - this code is deprecated.
# Scott says that we don't want to upsample anymore...
#
# $dem_type = get_dem_type($log);
# if ($dem_type eq "SRTMGL3") {
#  print "\nOnly a low resolution DEM source is available for this scene: $dem_type\n";
#  $lo_flg = 1;
#  $res = 30.0;
# }
#elsif ($dem_type eq "NED1" || $dem_type eq "NED2" || $dem_type eq "SRTMUS1" || $dem_type eq "SRTMAU1" || $dem_type eq "SRTMGL1") {
#  if (!$lo_flg) {
#    print "\nCreating 30 meter product and upsampling to $res meters\n";
#    $res = 30.0;
#    $mid_flg = 1;
#  }
#}

#
# Start processing the scene
#
my $num_vv = 0;
my @vv = glob "*/*/*vv*.tiff";
foreach my $v ( @vv ) { ++$num_vv; }
if ($num_vv == 1) { 
  print "\nFound VV polarization - processing\n\n"; 
  $pol = "vv";
  $main_pol = "vv";
  process_pol("$pol","$res","$no_match_flg","$dead_flg","$gamma_flg","$kmz_res","$output","$mode","$log");
  if ($mid_flg) { upsample_pol("$pol","$output","$gamma_flg","$mode"); }
}

my $num_vh = 0;
my @vh = glob "*/*/*vh*.tiff";
foreach my $v ( @vh ) { ++$num_vh; }
if ($num_vh == 1) { 
  print "\nFound VH polarization - processing\n\n"; 
  $pol = "vh";
  process_2nd_pol("$pol","$res","$gamma_flg","$kmz_res","$output","$mode","$dem","$log");
  if ($mid_flg) { upsample_pol("$pol","$output","$gamma_flg","$mode"); }
}

my $num_hh = 0;
my @hh = glob "*/*/*hh*.tiff";
foreach my $h ( @hh ) { ++$num_hh; }
if ($num_hh == 1) { 
  print "\nFound HH polarization - processing\n\n"; 
  $pol = "hh";
  $main_pol = "hh";
  process_pol("$pol","$res","$no_match_flg","$dead_flg","$gamma_flg","$kmz_res","$output","$mode","$log");
  if ($mid_flg) { upsample_pol("$pol","$output","$gamma_flg","$mode"); }
}

my $num_hv = 0;
my @hv = glob "*/*/*hv*.tiff";
foreach my $h ( @hv ) { ++$num_hv; }
if ($num_hv == 1) { 
  print "\nFound HV polarization - processing\n\n"; 
  $pol = "hv";
  process_2nd_pol("$pol","$res","$gamma_flg","$kmz_res","$output","$mode","$dem","$log");
  if ($mid_flg) { upsample_pol("$pol","$output","$gamma_flg","$mode"); }
}

if (($num_vv == 1 && $num_vh == 1) || ($num_hh == 1 && $num_hv == 1))
{
  $multi_pol = 1;
  if ($num_vv == 1)  { $cross_pol = "vh"; }
  else { $cross_pol = "hv"; }
} 

#
# Create browse, geo jpg, kmz
#
if ($multi_pol==1) {
  if ($num_vv == 1) { $pol1 = "vv"; $pol2 = "vh"; $CPOL1 = "VV"; $CPOL2 = "VH"; }
  elsif ($num_hh == 1) { $pol1 = "hh"; $pol2 = "hv"; $CPOL1 = "HH"; $CPOL2 = "HV"; }
  else {die "ERROR: No vv or hh pol found\n";}

  execute("cleanup_pixel 0.0039811 0.0 0.0 geo_${pol1}/${output}_${pol1}_${kmz_res}m.img ${output}_${pol1}_${kmz_res}m_cleaned.img",$log);
  execute("cleanup_pixel 0.0039811 0.0 0.0 geo_${pol2}/${output}_${pol2}_${kmz_res}m.img ${output}_${pol2}_${kmz_res}m_cleaned.img",$log);
  execute("color_browse -noise-cal -24 ${output}_${pol1}_${kmz_res}m_cleaned.img ${output}_${pol2}_${kmz_res}m_cleaned.img ${output}_hires_browse",$log);
  execute("asf_export -format geotiff -rgb Ps Pv Pd -byte TRUNCATE ${output}_hires_browse ${output}_hires.tif",$log);

  execute("color_browse -noise-cal -24 geo_${pol1}/${output}_${pol1}_browse geo_${pol2}/${output}_${pol2}_browse ${output}_browse",$log);
  execute("stats -nostat -overmeta -mask 0 ${output}_browse",$log);
  execute("asf_export -format geotiff -rgb Ps Pv Pd -byte TRUNCATE ${output}_browse ${output}.tif",$log);
 
  my $outdir = "PRODUCT";
  if ($res == 30.0) { $outname = "s1$plat-$mode-rtcm-$output"; }
  else { $outname = "s1$plat-$mode-rtch-$output"; }

  if ($kmz_flg) {
    execute("makeAsfBrowse.py ${output}_hires.tif ${outdir}/${outname}",$log);
  } else {
    execute("makeAsfBrowse.py ${output}.tif ${outdir}/${outname}",$log);
  }
} else {
  $pol = $main_pol;
  chdir("geo_${pol}");
  my $outdir = "../PRODUCT";

  execute("sqrt_img ${output}_${pol}_browse ${output}_amp_browse",$log);
  execute("asf_export -format geotiff -byte sigma ${output}_amp_browse ${output}.amp.tif",$log);

  if ($res == 30.0) { $outname = "s1$plat-$mode-rtcm-$output"; }
  else { $outname = "s1$plat-$mode-rtch-$output"; }

  if ($kmz_flg) {
    execute("makeAsfBrowse.py ${output}_${pol}_${kmz_res}m.tif ${outname}",$log);
  } else {
    execute("makeAsfBrowse.py ${output}.amp.tif ${outname}",$log);
  }
  print("Moving browse images to ");
  move("${outname}.kmz","$outdir/${outname}.kmz") or die "ERROR $0: Move failed: $!";
  move("${outname}.png","$outdir/${outname}.png") or die "ERROR $0: Move failed: $!";
  move("${outname}.png.aux.xml","$outdir/${outname}.png.aux.xml") or die "ERROR $0: Move failed: $!";
  move("${outname}_large.png","$outdir/${outname}_large.png") or die "ERROR $0: Move failed: $!";
  move("${outname}_large.png.aux.xml","$outdir/${outname}_large.png.aux.xml") or die "ERROR $0: Move failed: $!";

  chdir("..");

}

if ($res == 30.0) {
  $hdf5_list_name = "hdf5_list_rtcm.txt";
  $outname = "s1$plat-$mode-rtcm-$output";
  $outfile = "s1$plat-$mode-rtcm-$main_pol-$output";
} else { 
  $hdf5_list_name = "hdf5_list_rtch.txt";
  $outname = "s1$plat-$mode-rtch-$output";
  $outfile = "s1$plat-$mode-rtch-$main_pol-$output";
} 

generate_xml($hdf5_list_name,$outname,$main_pol,$outfile,$multi_pol,$cross_pol,$output,$log,$dem_type);

if ($mid_flg == 1) {
  $hdf5_list_name = "hdf5_list_rtch.txt";
  $outname = "s1$plat-$mode-rtch-$output";
  $outfile = "s1$plat-$mode-rtch-$main_pol-$output";
  generate_xml($hdf5_list_name,$outname,$main_pol,$outfile,$multi_pol,$cross_pol,$output,$log,$dem_type);
}

#Create consolidated log file
$out = "PRODUCT";
$new_basename = "s1$plat-$mode-rtcm-$output";
print("Creating log file: $out/$new_basename.log\n");
$logname = "$out/$new_basename.log";
open (LOG, ">$logname") or died("ERROR: Could not open consolidated log file: $logname: $!");
print LOG "Consolidated log for: $output\n";
my $options_string = "";

$options_string .= "-l " if $lo_flg;
$options_string .= "-h " if $kmz_flg;
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
  my ($hdf5_list_name,$outname,$main_pol,$outfile,$multi_pol,$cross_pol,$output,$log,$dem_type) = @_;

  # Create necessary meta file
  my @list = glob "S1*.SAFE";
  for (@list) {
 	$path = $_;
  }

  print "found path $path\n";

  $etc_dir = dirname($0) . "/../etc";
  copy("$etc_dir/sentinel_xml.xsl","sentinel_xml.xsl") or die ("ERROR $0: Copy failed: $!");

  $cmd = "xsltproc --stringparam path $path --stringparam timestamp timestring --stringparam file_size 1000 --stringparam server stuff --output out.xml sentinel_xml.xsl $path/manifest.safe";
  execute($cmd,$log);

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

  $out = "PRODUCT";
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

}

#
# Routine to upsample a pol using previsouly generated mapping information
# Creates main high res tif file, dem, inc_map, and ls_map
#
sub upsample_pol() {
  my ($pol,$output,$gamma_flg,$mode) = @_;
  $post = 10;
  print "\nUpsampling $pol polarization to 10 meters\n\n";

  my $main_pol;
  if ($pol eq "hv")    { $main_pol = "hh"; }
  elsif ($pol eq "vh") { $main_pol = "vv"; }

  $geo_dir = "geo_$pol";
  $gc0 = "$geo_dir/image_0.map_to_rdc";

  $up_dir = ${geo_dir}."_upsample";

  unless (-d $up_dir) {
    print "creating directory for output upsampled geocoded image products: $up_dir\n";
    $exit = system("mkdir $up_dir");
    $exit == 0 or die "ERROR $0: non-zero exit status: mkdir $up_dir\n";
  }

  $sim = "$up_dir/image.pix";
  my $dem = "area.dem";

  if ($pol eq "hv" or $pol eq "vh") {
    $dem_seg = "geo_${main_pol}/area.dem";
    $dem_seg_par = "geo_${main_pol}/area.dem_par";
  } else {
    $dem_seg = "$geo_dir/area.dem";
    $dem_seg_par = "$geo_dir/area.dem_par";
  }

  $dem_seg2= $up_dir."\/".$dem."_seg.dem";
  $dem_seg2_par = $dem_seg2.".par";

  $gc1 = "$geo_dir/image_1.map_to_rdc";
  $gc2 = "$up_dir/image.map_to_rdc";

  $ls_map = "$geo_dir/image_0.ls_map";
  $inc_map = "$geo_dir/image_0.inc_map";

  $mli = "$output.$pol.mgrd";
  $mli2 = "$output.$pol.GRD";

  $mli_par = "$output.$pol.mgrd.par";
  $mli2_par = "$output.$pol.GRD.par";

  execute("data2geotiff $dem_seg_par $ls_map 5 ls_map.tif","$log");
  execute("asf_import -format geotiff ls_map.tif ls_map","$log");
  execute("stats -overstat -overmeta ls_map",$log);
  execute("asf_geocode -p utm -ps $post -f ls_map ls_map_tmp","$log");

  execute("data2geotiff $dem_seg_par $inc_map 2 inc_map.tif","$log");
  execute("asf_import -format geotiff inc_map.tif inc_map","$log");
  execute("stats -overstat -overmeta -mask 0 inc_map",$log);
  execute("asf_geocode -p utm -ps $post -f -resample-method bicubic inc_map inc_map_tmp","$log");

  execute("map_section $dem_seg_par - - - - -$post $post $dem_seg2_par $gc1 $mli_par $mli2_par 0 $gc2 $up_dir/MLI_coord","$log");
  execute("dem_trans $dem_seg_par $dem_seg $dem_seg2_par $dem_seg2 - -","$log");

  # Create the correct size ls_map and inc_map
  @dem_seg_width = extract_param($dem_seg2_par,"width:");
  @dem_seg_lines = extract_param($dem_seg2_par,"nlines:");
  execute("trim -height $dem_seg_lines[1] -width $dem_seg_width[1] ls_map_tmp ls_map_big 0 0","$log");
  execute("trim -height $dem_seg_lines[1] -width $dem_seg_width[1] inc_map_tmp inc_map_big 0 0","$log");

  $ENV{OMP_NUM_THREADS} = '2';

  if ($gamma_flg ==1) {
    execute("pixel_area $mli2_par $dem_seg2_par $dem_seg2 $gc2 ls_map_big.img inc_map_big.img - $sim", $log);
  } else {
    execute("pixel_area $mli2_par $dem_seg2_par $dem_seg2 $gc2 - - $sim","$log");
  }

  $ENV{OMP_NUM_THREADS} = '4';

  $ellip_cal = $mli.".ellipse_cal";
  $ellip = "$up_dir/image.pix_ellipse";

  $ratio = "$up_dir/image.ratio_sigma0";
  $pix_cal = "$up_dir/image.pix_cal";

  $cal_mli = "$up_dir/image_cal_map.mli";
  $cal_tif = "$up_dir/image_cal_map.tif";

  @width = extract_param($mli2_par, "range_samples:");
  execute("radcal_MLI $mli2 $mli2_par - $ellip_cal - 0 0 1 0.0 - $ellip","$log");
  execute("ratio $ellip $sim $ratio $width[1] 1 1","$log");
  execute("product $mli2 $ratio $pix_cal $width[1] 1 1","$log");

  @dem_seg_width = extract_param($dem_seg2_par,"width:");
  @dem_seg_lines = extract_param($dem_seg2_par,"nlines:");

  execute("geocode_back $pix_cal $width[1] $gc2 $cal_mli $dem_seg_width[1] $dem_seg_lines[1] 2 0","$log");
  execute("raspwr $pix_cal $dem_seg_width[1] 1 0 1 1 1.0 0.4 1 $mli2.bmp","$log");

  execute("data2geotiff $dem_seg2_par $cal_mli 2 $cal_tif","$log");
  execute("data2geotiff $dem_seg2_par ls_map_big.img 5 ls_map_big.tif","$log");
  execute("data2geotiff $dem_seg2_par inc_map_big.img 2 inc_map_big.tif","$log");
  execute("data2geotiff $dem_seg2_par $dem_seg2 2 outdem.tif",$log);
  execute("gdal_translate -ot Int16 outdem.tif ${output}_${post}m.dem.tif",$log);
  
  my $outname = "s1$plat-$mode-rtch-$pol-$output";
  copy("$cal_tif","PRODUCT/$outname.tif") or die ("ERROR $0: Copy failed: $!");
  $outname = "s1$plat-$mode-rtch-$output";
  copy("ls_map_big.tif","PRODUCT/${outname}-ls_map.tif") or die ("ERROR $0: Copy failed: $!");
  copy("inc_map_big.tif","PRODUCT/${outname}-inc_map.tif") or die ("ERROR $0: Copy failed: $!");
  copy("${output}_${post}m.dem.tif","PRODUCT/${outname}-dem.tif") or die ("ERROR $0: Copy failed: $!");

}




#
# terrain geocode the cross-pol channel using the refinement information from the main channel
# thus bypassing modes 0, 1, and 2 of mk_geo_radcal
# creates the main cross-pol tif file
#
sub process_2nd_pol() {
  my ($pol2,$res,$gamma_flg,$kmz_res,$output,$mode,$dem,$log) = @_;
  if ($pol2 eq "hv") { $pol1 = "hh"; }
  else { $pol1 = "vv"; }

  my $options = "-p -j -n 6 -q -c ";
  $options .= "-g " if $gamma_flg;

  print "Cross-pol is $pol2; Main pol is $pol1\n";

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
  execute("resample -size 1000 tc_$pol2 ${output}_${pol2}_browse",$log);
  execute("resample -square $kmz_res tc_$pol2 ${output}_${pol2}_${kmz_res}m",$log);
  fix_band_name("${output}_${pol2}_browse.meta",$pol);

  if ($res == 30.0) { $outname = "s1$plat-$mode-rtcm-$pol2-$output.tif"; }
  else { $outname = "s1$plat-$mode-rtch-$pol2-$output.tif"; }
  my $out = "../PRODUCT";

  print "Moving file image_cal_map.mli.tif to $out/$outname\n";
  move("image_cal_map.mli.tif","$out/$outname") or die "Move failed: image_cal_map.mli.tif -> ../$outname";

  chdir("..");

}

#
# Main routine to process a single pol of data
# Creates the main .tif file, the dem, ls_map, and inc_map
#
sub process_pol() {
  my ($pol,$res,$no_match_flg,$dead_flg,$gamma_flg,$kmz_res,$output,$mode,$log) = @_;

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
  execute("resample -size 1000 tc_$pol ${output}_${pol}_browse",$log);
  execute("resample -square $kmz_res tc_$pol ${output}_${pol}_${kmz_res}m",$log);
  execute("asf_export -format geotiff ${output}_${pol}_${kmz_res}m ${output}_${pol}_${kmz_res}m.tif",$log);
  fix_band_name("${output}_${pol}_browse.meta",$pol);

  my $out = "../PRODUCT";
  mkdir($out);

  if ($res == 30.0) { $outname = "s1$plat-$mode-rtcm-$pol-$output"; }
  else { $outname = "s1$plat-$mode-rtch-$pol-$output"; }

  move("image_cal_map.mli.tif","$out/$outname.tif") or die "Move failed: image_cal_map.mli.tif -> $out/$outname.tif";

  if ($res == 30.0) { $outname = "s1$plat-$mode-rtcm-$output"; }
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

#
# Fix the band names in a 3 banded ASF internal meta file
# by setting the band names equal to the polarizations
#
sub fix_three_banded {
  my ($metafile,$pol1,$pol2) = @_;
  $meta_output = `cat $metafile`;
  my @meta = split /\n/, $meta_output; #split into lines
  open(DPAR,"> tmp.meta") or die("ERROR $0: Cant create tmp meta file\n\n");
  foreach my $line (@meta){
    if ($line =~ m/bands:/) {
      print DPAR "    bands: $pol1,$pol2,DIV\n";
    } else {
      print DPAR "$line\n";
    }
  }
  close(DPAR);
  move("tmp.meta",$metafile) or die("ERROR $0: Move failed: $!");
}

sub get_dem_type {
  my ($log) = @_;
  open(LOG,$log) or die "ERROR $0: could not open log: $log: $!\n\n";
  my (@lines) = <LOG>;
  close(LOG);

  $dem_type = "";
  while (my $line = shift(@lines)) {
    if ($line =~ /Now generating tmpdem\.tif using (\w+)/) {
      $dem_type = $1;
      last;
    }
  }
  return $dem_type;
}

sub extract_param{
  my ($infile,$keyword) = @_;
  open(PAR_IN,$infile) || die "ERROR $0: cannot open parameter file: $infile\n";

  while(<PAR_IN>){
    chomp;
    @tokens = split;
    if($tokens[0] eq $keyword){close PAR_IN; return @tokens;}
  }
  close PAR_IN;
  die "ERROR $0: keyword $keyword not found in file: $infile\n";
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

