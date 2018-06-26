python -m cProfile -o profile_results.prof .\src\main.py --evolution-tests --profile
gprof2dot -f pstats profile_results.prof | dot -Tpng -o profile_results.png