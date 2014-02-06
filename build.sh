#!/bin/bash

shebang='#!/usr/bin/env python'

target="./troublestack_`date +%s`.py"


echo "${shebang}" > ${target}
chmod oug+x "${target}"


for f in ./files/* ; do
  fn=`basename ${f}`
  line="basefile['${fn}']"
  line="${line}='''`base64 ${f}`'''"
  echo "${line}" >> "${target}"
done

cat troublestack.py >> ${target}
