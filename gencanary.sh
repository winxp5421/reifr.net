#!/bin/bash

#Check for persistant increment file
if [ ~ -f ./count ] ; then
    HISTORY=0
else
    HISTORY=$(cat ./count)
fi

#increment by one
COUNT=`expr ${HISTORY} + 1`


echo "${COUNT}" > ./count


echo "                    ---===[ reifr.net canary #$HISTORY ]===---


Statements
-----------
The administrators of reifr.net who have digitally signed this file state the following:


1. The date of issue of this canary is $(date -u +%x)

2. The reifr.net Master Signing Key fingerprint is:

	20BB 6616 A328 2A9F 8F15 9A53 4BB8 D801 C141 7BDC

3. No warrants have ever been served to us with regard to the reifr.net
domain or subdomains (e.g. to hand out private data related to the domain's
SSL certificates, signing keys, encrypted files, or non-encrypted files, user data,
or hardware the services are running on).

4. We plan to publish the next of these canary statements in the first
two weeks of $(date -u +'%B %Y' -d "+6 months"). Special note should be taken if no new canary
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
$(date -R -u)

$ feedstail -1 -n5 -f '{title}' -u https://www.spiegel.de/international/index.rss
$(feedstail -1 -n5 -f '{title}' -u https://www.spiegel.de/international/index.rss)

$ feedstail -1 -n5 -f '{title}' -u https://rss.nytimes.com/services/xml/rss/nyt/World.xml
$(feedstail -1 -n5 -f '{title}' -u https://rss.nytimes.com/services/xml/rss/nyt/World.xml)

$ feedstail -1 -n5 -f '{title}' -u https://feeds.bbci.co.uk/news/world/rss.xml
$(feedstail -1 -n5 -f '{title}' -u https://feeds.bbci.co.uk/news/world/rss.xml)

$ feedstail -1 -n5 -f '{title}' -u http://feeds.reuters.com/reuters/worldnews
$(feedstail -1 -n5 -f '{title}' -u http://feeds.reuters.com/reuters/worldnews)

$ python3 -c 'import sys, json; print(json.load(sys.stdin)['\''blocks'\''][10]['\''hash'\''])'
$ curl -s 'https://blockchain.info/blocks/?format=json'
$(curl -s 'https://blockchain.info/blocks/?format=json' | python3 -c 'import sys, json; print(json.load(sys.stdin)['\''blocks'\''][10]['\''hash'\''])')

Footnotes
----------

[1] This file should be signed via detached PGP
signatures by each of the signers, distributed together with this
canary in the https://github.com/winxp5421/reifr.net.git repository. [2]

[2] Don't just trust the contents of this file blindly! Verify the
digital signatures!"

