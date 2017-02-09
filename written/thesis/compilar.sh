#!/bin/bash

# Genero los circuitos del Informe si me ingresan la opción indicada
if [ "$1" == "-c" ] ; then
	 ./Circuitos/compilarCircuitos.sh
fi

nombre="main"
# Compilo dos veces para que aparezca el índice
pdflatex --shell-escape $nombre.tex 
bibtex $nombre.aux
pdflatex --shell-escape $nombre.tex
pdflatex --shell-escape $nombre.tex

# Borro los archivos auxiliares
rm $nombre.toc $nombre.aux $nombre.log $nombre.out 
