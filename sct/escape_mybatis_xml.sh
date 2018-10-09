#!/bin/bash
## TODO use keywords for replace, ex> isNotEmpty, isNotNull

for filename in `find . -maxdepth 6 -type f -name "*.xml"`; do
        echo "${filename}"
	grep " </dynamic>" ${filename}
	#diff $filename ${filename}.bak
	cp $filename ${filename}.bak
	sed -e 's/#{\([a-zA-Z0-9\-\_]*\)}/:\1/g' $filename | sed -e 's/#\([a-zA-Z0-9\-\_]*\)#/:\1/g' | sed -e 's/<if test=.*>//g' | sed -e 's/<\/if>//g' | sed -e '/<foreach collection/,/<\/foreach>/d' | sed -e 's/<isNotNull .*>//g' | sed -e 's/<\/isNotNull>//g' | sed -e 's/<isNotEmpty.* prepend="\([ a-zA-Z]*\)".*>/ \1 /g' | sed -e 's/<\/isNotEmpty>//g' | sed -e 's/<isEqual.* prepend="\([ a-zA-Z]*\)".*>/ \1 /g' | sed -e 's/<\/isEqual>//g' | sed -e 's/<isNotEqual.* prepend="\([ a-zA-Z]*\)".*>/ \1 /g' | sed -e 's/<\/isNotEqual>//g' | sed -e 's/<isNotEmpty.*>//g' | sed -e 's/<isNotNull.*>//g' | sed -e 's/<isNotEqual.*>//g' | sed -e 's/<isEqual.*>//g' | sed -e 's/<isEmpty.*>//g' | sed -e 's/<\/isEmpty>//g' > $filename
        xmllint --xpath '//sql/text()' ${filename} 
	grep " prepend=" ${filename}
done

