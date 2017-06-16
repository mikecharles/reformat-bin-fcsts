clean:
	rm -rf ./venv

develop:
	if ! ls -l venv >& /dev/null ; then \
			conda create --no-default-packages --yes -p ./venv python=3 ; \
	fi
	( source activate ./venv && conda install --yes --file conda-requirements.txt )
	( source activate ./venv && conda install --yes -c conda-forge basemap )
	( source activate ./venv && pip install -r pip-requirements.txt )
