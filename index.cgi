#!/usr/bin/perl -w

use CGI;                             # load CGI routines
$CGI::POST_MAX = 160 * 40;  	    # max 160rows/40cols post
$CGI::DISABLE_UPLOADS = 1;          # no uploads

# File Paths
$SHALLAPATH="/var/www/shalla";
$CATEGORYFILE=$SHALLAPATH."/shallacategories.txt";
$BLOCKFILE=$SHALLAPATH."/shallablock.txt";
$WHITELISTFILE=$SHALLAPATH."/whitelist.txt";
$BLACKLISTFILE=$SHALLAPATH."/blacklist.txt";

# Regexps for sanitation
$BLOCKOK='-a-zA-Z0-9/';
$EXPLAINOK='-a-zA-Z0-9/.@ ';
$LISTOK=$EXPLAINOK.'\n';

$q = CGI->new;
print $q->header,                    # create the HTTP header
	$q->start_html('Shalla List Config'); # start the HTML

# Error if there is no category file
sub nocategories {
	print $q->h1('no category file');         # level 1 header
	print $q->end_html;                  # end the HTML
	die ("File $CATEGORYFILE not found !\n");
}

# Read category list
open(my $fh, '<', $CATEGORYFILE) or nocategories();
while ($inline=<$fh>){
	chomp $inline;
	@cats=split / /,$inline;
	$mycat=shift @cats;
	$mycat=~s/[^$BLOCKOK]//go;
	$category{$mycat}=0;
	$inline=join " ",@cats;
	$inline=~s/[^$EXPLAINOK]//go;
	$explain{$mycat}="<span title=\"".$inline."\">".$mycat."</span>";
}
close $fh;

# Read list of currently blocked categories if present
if ( -f $BLOCKFILE ){
	open(my $fh, '<', $BLOCKFILE);
	while ($inline=<$fh>){
		chomp $inline;
		@bla=split / /,$inline;
		$bla[0]=~s/[^$BLOCKOK]//go;
		push @blocked,$bla[0];
	}
	close $fh;
} else {
	@blocked="";
}

# Read current whitelist if present
if ( -f $WHITELISTFILE ){
	open(my $fh, '<', $WHITELISTFILE);
        while ($inline=<$fh>){
                chomp $inline;
                @bla=split / /,$inline;
                $bla[0]=~s/[^$LISTOK]//go;
                push @whitelist,$bla[0];
        }
        close $fh;
} else {
        @whitelist="";
}
$mywhitelist="";
while($dummy=shift @whitelist){
        $mywhitelist.=$dummy."\n";
}
chomp $mywhitelist;

# Read current blacklist if present
if ( -f $BLACKLISTFILE ){
        open(my $fh, '<', $BLACKLISTFILE);
        while ($inline=<$fh>){
                chomp $inline;
                @bla=split / /,$inline;
                $bla[0]=~s/[^$LISTOK]//go;
                push @blacklist,$bla[0];
        }
        close $fh;
} else {
        @blacklist="";
}
$myblacklist="";	
while($dummy=shift @blacklist){
	$myblacklist.=$dummy."\n";
}
chomp $myblacklist;

print $q->h1('Web Blocker');      
print $q->h2('Blocked categories'); 
print $q->h4('Hover over a categories\' name to see a short explanation');
print $q->start_form;

# If there are no parameters, show a formto select categories
if (!$q->param) {
	print CGI::unescapeHTML($q->checkbox_group(
        	-name     => 'blocked',
	        -values   => [sort keys %category],
		-labels	  => \%explain,
		-defaults => \@blocked,
	        -columns  => 6,
	    ));
        print $q->h2('Whitelist');
        print $q->textarea(
                -name  => 'whitelist',
                -value => $mywhitelist,
                -cols  => 60,
                -rows  => 3,
        );
	print $q->h2('Blacklist'); 
	print $q->textarea(
       	 	-name  => 'blacklist',
        	-value => $myblacklist,
        	-cols  => 60,
        	-rows  => 3,
    	);
	print $q->submit(-value=>'Submit categories');
# If parameters are present, show selected stuff, write files and go back 
} else {
# Write list of currently blocked categories
	open(my $fh, '>', $BLOCKFILE) or die ("Could not write Blockfile !\n");
	print $q->h1('The following categories are blocked:');
	@blocked = $q->param('blocked');

	print "<BLOCKQUOTE>\n";
	foreach $block (sort @blocked) {
		$block=~s/[^$BLOCKOK]//go;
		print $explain{$block}."<BR>";
		print $fh $block."\n";
	}
	print "</BLOCKQUOTE>\n";
	close $fh;
# Write current whitelist
	open(my $fh, '>', $WHITELISTFILE) or die ("Could not write Whitelistfile !\n");
	print $q->h1('Whitelisted sites:');
	print "<BLOCKQUOTE>\n";
        $mywhitelist=$q->param('whitelist');
        $mywhitelist=~s/[^$LISTOK]//go;
	@bla=split /[[:space:]]+/,$mywhitelist;
	while ($dummy=shift @bla){
		print $dummy."<br>\n";
		print $fh $dummy."\n";
	}
	print "</BLOCKQUOTE>\n";
	close $fh;
# Write current blacklist
	open(my $fh, '>', $BLACKLISTFILE) or die ("Could not write Blacklistfile !\n");
        print $q->h1('Blacklisted sites:');
        print "<BLOCKQUOTE>\n";
        $myblacklist=$q->param('blacklist');
        $myblacklist=~s/[^$LISTOK]//go;
	@bla=split /[[:space:]]+/,$myblacklist;
	while ($dummy=shift @bla){
		print $dummy."<br>\n";
		print $fh $dummy."\n";
	}
	print "</BLOCKQUOTE>\n";
	close $fh;

	print $q->submit(-value=>'OK');

}
print $q->end_form;
print $q->end_html;                  # end the HTML
