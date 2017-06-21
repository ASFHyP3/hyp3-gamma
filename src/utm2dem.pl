#!/usr/bin/perl
use FileHandle;
use File::Basename;

$pixasarea = 0;

if (($#ARGV + 1) < 3){die <<EOS ;}
*** $0
*** Copyright 2012, Gamma Remote Sensing, v1.0 29-Aug-2012 clw ***
*** Modified by T. Logan, Jan 2014
*** Convert UTM DEM tile (GEOTIFF) to Gamma format DEM and DEM parameter file ***

usage: $0 <UTM_DEM> <DEM> <DEM_par>
    UTM_DEM   (input)  UTM DEM data
    DEM       (output) DEM data (short integer)
    DEM_par   (output) Gamma DEM parameter file

EOS

$utm = $ARGV[0];
$dem     = $ARGV[1];
$dem_par = $ARGV[2];
$dem_par_in = "dem_par.in";
$utm_tmp= "utm_tmp";
$utm_tmp2 = "utm_tmp2";

my ($s1, $dir1, $ext1) = fileparse($utm, qr/\.[^.]*/); #extension is the last bit after the last period
print "basename: $s1\n";
$log = "$s1"."_utm_dem.log";

print "UTM DEM in GEOTIFF format: $utm\n";
print "output DEM: $dem\n";
print "output DEM parameter file: $dem_par\n";
print "log file: $log\n";

$gdal_output = `gdalinfo $utm`;
#print $gdal_output;

my @gdal = split /\n/, $gdal_output; #split into lines

foreach my $line (@gdal){
  if ($line =~ m/Size is/) {
    @a = split (/[\s+,]/, $line);	#parse line into tokens, splitting on whitespace or ,
    $xsize = $a[2];
    $ysize = $a[4];
    print "\nDEM samples across: $xsize   down: $ysize\n";
  }

  if ($line =~ m/PROJCS/) {
    @a = split(/[ ,]/, $line);		#parse line into tokens, splitting on white space or ,
    $a[5] =~ /([0-9]+)(.)(.)/;		#parse token into number, other, other
    $zone = $1;				#grad the number that was just parsed
    print "Found zone number: $zone\n";
  }

  if ($line =~ m/Upper Left/) {
    @a = split (/[(),]/, $line);	#parse line into tokens, splitting on (),
    $east = $a[1];
    $north = $a[2];
    print "Upper Left corner northing (m): $north    easting (m): $east\n";
  }

  if ($line =~ m/Pixel Size/){
    @a = split (/[(),]/, $line);	#parse line into tokens, splitting on (),
    $pix_east = $a[1];
    $pix_north = $a[2];
    print "Pixel Size (m) northing: $pix_north    easting: $pix_east\n";
  }

  if ($line =~ m/false_northing/){
    @a = split (/[(),]/, $line);	#parse line into tokens, splitting on (),
    $false_north = $a[1];
    print "False northing: $false_north\n";
  }

  if ($line =~ /  AREA_OR_POINT=Area/){
    $pixasarea = 1;
  }
}

if ($pixasarea == 1){
  print "\nPixel as Area! updating corner coordinates to pixel as point\n";
  print "pixel upper northing (m): $north    easting (m): $east\n";
  $east = $east + $pix_east/2.0;
  $north = $north + $pix_north/2.0;
  print "updated pixel upper northing (m): $north    easting (m): $east\n";
}
$pix_size = $pix_east;
print "approximate DEM latitude pixel spacing (m): $pix_size\n"; 

open(DPAR, "> $dem_par_in") or die "ERROR $0: cannot create file with inputs to create_dem_par: $dem_par_in\n\n";
print DPAR "UTM\nWGS84\n1\n$zone\n$false_north\n$s1\nREAL*4\n0.0\n1.0\n$xsize\n$ysize\n$pix_north $pix_east\n$north $east\n";
close(DPAR);
print "\n";
execute("rm -f $dem_par",$log);
execute("create_dem_par $dem_par < $dem_par_in",$log);
print "\n\n";

execute("gdal_translate -of ENVI $utm  $utm_tmp",$log);
execute("swap_bytes $utm_tmp $dem 4", $log);
execute("replace_values $dem 0 -1  $utm_tmp  $xsize 0 2", $log);
execute("replace_values $utm_tmp -32767 -1  $utm_tmp2  $xsize 0 2", $log);
execute("replace_values $utm_tmp2 -32768 -1  $dem  $xsize 0 2", $log);
execute("/bin/rm -f $utm_tmp",$log);
execute("/bin/rm -f $utm_tmp2",$log);
exit(0);

sub execute{
  my ($command, $log) = @_;
  print "$command\n";

  my $out = `$command`;
  my $exit = $? >> 8;

  if (-e $log){open(LOG,">>$log") or die "ERROR $0: cannot open log file: $log  command: $command\n";}
  else {open(LOG,">$log") or die "ERROR $0 : cannot open log file: $log  command: $command\n";}
  LOG->autoflush;
  print LOG ("\nRunning: ${command}\nOutput:\n${out}\n----------\n");
  close LOG;
  if ($exit != 0) { print "\nnon-zero exit status: ${command}\nOutput:\n${out}\n"; }
  $exit == 0 or die "ERROR $0: non-zero exit status: $command\n"
}

