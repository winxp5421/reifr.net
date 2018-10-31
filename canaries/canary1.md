                    ---===[ reifr.net Canary #1 ]===---


Statements
-----------
The Administrators of reifr.net who have digitally signed this file state the following:


1. The date of issue of this canary is 10/30/2018

2. There have been 1 reifr.net Security Bulletins published so far.

3. The reifr.net Master Signing Key fingerprint is:

	20BB 6616 A328 2A9F 8F15 9A53 4BB8 D801 C141 7BDC

4. No warrants have ever been served to us with regard to the reifr.net
domain or subdomains (e.g. to hand out private data related to the domain's
SSL certificates, signing keys, encrypted files, or non-encrypted files, user data,
or hardware the services are running on).

5. We plan to publish the next of these canary statements in the first
two weeks of April 2019. Special note should be taken if no new canary
is published by that time or if the list of statements changes without
plausible explanation.

Special announcements
----------------------

None.

Disclaimers and notes
----------------------

This canary scheme is not infallible. Although signing the declaration
makes it very difficult for a third party to produce arbitrary
declarations, it does not prevent them from using force or other
means, like blackmail or compromising the signers' laptops, to coerce
us to produce false declarations.

The news feeds quoted below (Proof of freshness) serves to demonstrate
that this canary could not have been created prior to the date stated.
It shows that a series of canaries was not created in advance.

This declaration is merely a best effort and is provided without any
guarantee or warranty. It is not legally binding in any way to
anybody. None of the signers should be ever held legally responsible
for any of the statements made here.

Proof of freshness
-------------------

$ date -R -u
Wed, 31 Oct 2018 01:50:43 +0000

$ feedstail -1 -n5 -f '{title}' -u https://www.spiegel.de/international/index.rss
Facing Up to Anti-Semitism: 'We Will Win Because History Is On Our Side'
A New Cold War? U.S. Withdrawal from Nuke Treaty Worries Europeans
Brexit Talks: It's Time to Make Concessions to Britain
The Stephen Bannon Project: Searching in Europe for Glory Days Gone By
Interview with Italian Vintner Antinori: 'Italian Wines Are Drunk, Not Collected'

$ feedstail -1 -n5 -f '{title}' -u https://rss.nytimes.com/services/xml/rss/nyt/World.xml
As Merkel Eyes Exit, Nervous E.U. Wonders Who’ll Take the Stage
Indonesia Plane Crash Leaves Experts Puzzled
Senior Saudi Prince Returns to Kingdom as Royals Confront Khashoggi Crisis
As World’s Air Gets Worse, India Struggles to Breathe
Venice Flooding Is Worst in a Decade; Severe Weather in Italy Kills at Least 11

$ feedstail -1 -n5 -f '{title}' -u https://feeds.bbci.co.uk/news/world/rss.xml
Pittsburgh shooting: Trump visits synagogue amid protests
Gangster James 'Whitey' Bulger killed in prison
Venice under water as deadly storms hit Italy
Denmark accuses Iran of activist murder plot
Father of 'Jihadi Jack' asks Canada to help bring son home

$ feedstail -1 -n5 -f '{title}' -u http://feeds.reuters.com/reuters/worldnews
U.S. general says troop numbers at Mexican border to rise further
Thousands of Venezuelans head to Peru to beat residency deadline
U.S.'s Pompeo calls for end of fighting in Yemen
Bolsonaro's economic guru urges quick Brazil pension reform
U.N. chief taps Norwegian diplomat as new Syria envoy: letter

$ python3 -c 'import sys, json; print(json.load(sys.stdin)['\''blocks'\''][10]['\''hash'\''])'
$ curl -s 'https://blockchain.info/blocks/?format=json'
000000000000000000167ae7cc59e577d094c450fb730477f157bdaba68212c3

Footnotes
----------

[1] This file should be signed via detached PGP
signatures by each of the signers, distributed together with this
canary in the https://github.com/winxp5421/reifr.net.git repository. [2]

[2] Don't just trust the contents of this file blindly! Verify the
digital signatures!
