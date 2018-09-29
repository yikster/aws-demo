#!/bin/bash
## TODO use keywords for replace, ex> isNotEmpty, isNotNull
for filename in `ls *.xml`; do
	cp $filename ${filename}.bak
	sed -e 's/#{\([a-zA-Z0-9\-\_]*\)}/:\1/g' $filename | sed -e 's/#\([a-zA-Z0-9\-\_]*\)#/:\1/g' | sed -e 's/<\!\[CDATA\[//g' | sed -e 's/\]\]>//g' | sed -e 's/<if test=.*>//g' | sed -e 's/<\/if>//g' | sed -e '/<foreach collection/,/<\/foreach>/d' | sed -e 's/<isNotNull property=.*>//g' | sed -e 's/<\/isNotNull>//g' | sed -e 's/<isNotEmpty property=.*>//g' | sed -e 's/<\/isNotEmpty>//g' > $filename
done

