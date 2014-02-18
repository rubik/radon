def solve(f, *symbols, **flags):
    def _sympified_list(w):
        return list(map(sympify, w if iterable(w) else [w]))
    bare_f = not iterable(f)
    ordered_symbols = (symbols and
                       symbols[0] and
                       (isinstance(symbols[0], Symbol) or
                        is_sequence(symbols[0],
                        include=GeneratorType)
                       )
                      )
    f, symbols = (_sympified_list(w) for w in [f, symbols])

    implicit = flags.get('implicit', False)

    # preprocess equation(s)
    ###########################################################################
    for i, fi in enumerate(f):
        if isinstance(fi, Equality):
            f[i] = fi.lhs - fi.rhs
        elif isinstance(fi, Poly):
            f[i] = fi.as_expr()
        elif isinstance(fi, bool) or fi.is_Relational:
            return reduce_inequalities(f, assume=flags.get('assume'),
                                       symbols=symbols)

        # Any embedded piecewise functions need to be brought out to the
        # top level so that the appropriate strategy gets selected.
        # However, this is necessary only if one of the piecewise
        # functions depends on one of the symbols we are solving for.
        def _has_piecewise(e):
            if e.is_Piecewise:
                return e.has(*symbols)
            return any([_has_piecewise(a) for a in e.args])
        if _has_piecewise(f[i]):
            f[i] = piecewise_fold(f[i])

        # if we have a Matrix, we need to iterate over its elements again
        if f[i].is_Matrix:
            bare_f = False
            f.extend(list(f[i]))
            f[i] = S.Zero

        # if we can split it into real and imaginary parts then do so
        freei = f[i].free_symbols
        if freei and all(s.is_real or s.is_imaginary for s in freei):
            fr, fi = f[i].as_real_imag()
            if fr and fi and not any(i.has(re, im, arg) for i in (fr, fi)) \
                    and fr != fi:
                if bare_f:
                    bare_f = False
                f[i: i + 1] = [fr, fi]

    # preprocess symbol(s)
    ###########################################################################
    if not symbols:
        # get symbols from equations
        symbols = reduce(set.union, [fi.free_symbols
                                     for fi in f], set())
        if len(symbols) < len(f):
            for fi in f:
                pot = preorder_traversal(fi)
                for p in pot:
                    if not (p.is_number or p.is_Add or p.is_Mul) or \
                            isinstance(p, AppliedUndef):
                        flags['dict'] = True  # better show symbols
                        symbols.add(p)
                        pot.skip()  # don't go any deeper
        symbols = list(symbols)
        # supply dummy symbols so solve(3) behaves like solve(3, x)
        for i in range(len(f) - len(symbols)):
            symbols.append(Dummy())

        ordered_symbols = False
    elif len(symbols) == 1 and iterable(symbols[0]):
        symbols = symbols[0]

    # remove symbols the user is not interested in
    exclude = flags.pop('exclude', set())
    if exclude:
        if isinstance(exclude, Expr):
            exclude = [exclude]
        exclude = reduce(set.union, [e.free_symbols for e in sympify(exclude)])
    symbols = [s for s in symbols if s not in exclude]

    # real/imag handling
    for i, fi in enumerate(f):
        _abs = [a for a in fi.atoms(Abs) if a.has(*symbols)]
        fi = f[i] = fi.xreplace(dict(list(zip(_abs,
            [sqrt(a.args[0]**2) for a in _abs]))))
        if fi.has(*_abs):
            if any(s.assumptions0 for a in
                    _abs for s in a.free_symbols):
                raise NotImplementedError(filldedent('''
                All absolute
                values were not removed from %s. In order to solve
                this equation, try replacing your symbols with
                Dummy symbols (or other symbols without assumptions).
                ''' % fi))
            else:
                raise NotImplementedError(filldedent('''
                Removal of absolute values from %s failed.''' % fi))
        _arg = [a for a in fi.atoms(arg) if a.has(*symbols)]
        f[i] = fi.xreplace(dict(list(zip(_arg,
            [atan(im(a.args[0])/re(a.args[0])) for a in _arg]))))
    # see if re(s) or im(s) appear
    irf = []
    for s in symbols:
        # if s is real or complex then re(s) or im(s) will not appear in the equation;
        if s.is_real or s.is_complex:
            continue
        # if re(s) or im(s) appear, the auxiliary equation must be present
        irs = re(s), im(s)
        if any(_f.has(i) for _f in f for i in irs):
            symbols.extend(irs)
            irf.append((s, re(s) + S.ImaginaryUnit*im(s)))
    if irf:
        for s, rhs in irf:
            for i, fi in enumerate(f):
                f[i] = fi.xreplace({s: rhs})
        if bare_f:
            bare_f = False
        flags['dict'] = True
        f.extend(s - rhs for s, rhs in irf)
    # end of real/imag handling

    symbols = list(uniq(symbols))
    if not ordered_symbols:
        # we do this to make the results returned canonical in case f
        # contains a system of nonlinear equations; all other cases should
        # be unambiguous
        symbols = sorted(symbols, key=default_sort_key)

    # we can solve for non-symbol entities by replacing them with Dummy symbols
    symbols_new = []
    symbol_swapped = False
    for i, s in enumerate(symbols):
        if s.is_Symbol:
            s_new = s
        else:
            symbol_swapped = True
            s_new = Dummy('X%d' % i)
        symbols_new.append(s_new)

    if symbol_swapped:
        swap_sym = list(zip(symbols, symbols_new))
        f = [fi.subs(swap_sym) for fi in f]
        symbols = symbols_new
        swap_sym = dict([(v, k) for k, v in swap_sym])
    else:
        swap_sym = {}

    # this is needed in the next two events
    symset = set(symbols)

    # get rid of equations that have no symbols of interest; we don't
    # try to solve them because the user didn't ask and they might be
    # hard to solve; this means that solutions may be given in terms
    # of the eliminated equations e.g. solve((x-y, y-3), x) -> {x: y}
    newf = []
    for fi in f:
        # let the solver handle equations that..
        # - have no symbols but are expressions
        # - have symbols of interest
        # - have no symbols of interest but are constant
        # but when an expression is not constant and has no symbols of
        # interest, it can't change what we obtain for a solution from
        # the remaining equations so we don't include it; and if it's
        # zero it can be removed and if it's not zero, there is no
        # solution for the equation set as a whole
        #
        # The reason for doing this filtering is to allow an answer
        # to be obtained to queries like solve((x - y, y), x); without
        # this mod the return value is []
        ok = False
        if fi.has(*symset):
            ok = True
        else:
            free = fi.free_symbols
            if not free:
                if fi.is_Number:
                    if fi.is_zero:
                        continue
                    return []
                ok = True
            else:
                if fi.is_constant():
                    ok = True
        if ok:
            newf.append(fi)
    if not newf:
        return []
    f = newf
    del newf

    # mask off any Object that we aren't going to invert: Derivative,
    # Integral, etc... so that solving for anything that they contain will
    # give an implicit solution
    seen = set()
    non_inverts = set()
    for fi in f:
        pot = preorder_traversal(fi)
        for p in pot:
            if not isinstance(p, Expr) or isinstance(p, Piecewise):
                pass
            elif (isinstance(p, bool) or
                    not p.args or
                    p in symset or
                    p.is_Add or p.is_Mul or
                    p.is_Pow and not implicit or
                    p.is_Function and not implicit):
                continue
            elif not p in seen:
                seen.add(p)
                if p.free_symbols & symset:
                    non_inverts.add(p)
                else:
                    continue
            pot.skip()
    del seen
    non_inverts = dict(list(zip(non_inverts, [Dummy() for d in non_inverts])))
    f = [fi.subs(non_inverts) for fi in f]

    non_inverts = [(v, k.subs(swap_sym)) for k, v in non_inverts.items()]

    # rationalize Floats
    floats = False
    if flags.get('rational', True) is not False:
        for i, fi in enumerate(f):
            if fi.has(Float):
                floats = True
                f[i] = nsimplify(fi, rational=True)

    #
    # try to get a solution
    ###########################################################################
    if bare_f:
        solution = _solve(f[0], *symbols, **flags)
    else:
        solution = _solve_system(f, symbols, **flags)

    #
    # postprocessing
    ###########################################################################
    # Restore masked-off objects
    if non_inverts:

        def _do_dict(solution):
            return dict([(k, v.subs(non_inverts)) for k, v in
                         solution.items()])
        for i in range(1):
            if type(solution) is dict:
                solution = _do_dict(solution)
                break
            elif solution and type(solution) is list:
                if type(solution[0]) is dict:
                    solution = [_do_dict(s) for s in solution]
                    break
                elif type(solution[0]) is tuple:
                    solution = [tuple([v.subs(non_inverts) for v in s]) for s
                                in solution]
                    break
                else:
                    solution = [v.subs(non_inverts) for v in solution]
                    break
            elif not solution:
                break
        else:
            raise NotImplementedError(filldedent('''
                            no handling of %s was implemented''' % solution))

    # Restore original "symbols" if a dictionary is returned.
    # This is not necessary for
    #   - the single univariate equation case
    #     since the symbol will have been removed from the solution;
    #   - the nonlinear poly_system since that only supports zero-dimensional
    #     systems and those results come back as a list
    #
    # ** unless there were Derivatives with the symbols, but those were handled
    #    above.
    if symbol_swapped:
        symbols = [swap_sym[k] for k in symbols]
        if type(solution) is dict:
            solution = dict([(swap_sym[k], v.subs(swap_sym))
                             for k, v in solution.items()])
        elif solution and type(solution) is list and type(solution[0]) is dict:
            for i, sol in enumerate(solution):
                solution[i] = dict([(swap_sym[k], v.subs(swap_sym))
                              for k, v in sol.items()])

    # undo the dictionary solutions returned when the system was only partially
    # solved with poly-system if all symbols are present
    if (
            solution and
            ordered_symbols and
            type(solution) is not dict and
            type(solution[0]) is dict and
            all(s in solution[0] for s in symbols)
    ):
        solution = [tuple([r[s].subs(r) for s in symbols]) for r in solution]

    # Get assumptions about symbols, to filter solutions.
    # Note that if assumptions about a solution can't be verified, it is still
    # returned.
    check = flags.get('check', True)

    # restore floats
    if floats and solution and flags.get('rational', None) is None:
        solution = nfloat(solution, exponent=False)

    if check and solution:

        warning = flags.get('warn', False)
        got_None = []  # solutions for which one or more symbols gave None
        no_False = []  # solutions for which no symbols gave False
        if type(solution) is list:
            if type(solution[0]) is tuple:
                for sol in solution:
                    for symb, val in zip(symbols, sol):
                        test = check_assumptions(val, **symb.assumptions0)
                        if test is False:
                            break
                        if test is None:
                            got_None.append(sol)
                    else:
                        no_False.append(sol)
            elif type(solution[0]) is dict:
                for sol in solution:
                    a_None = False
                    for symb, val in sol.items():
                        test = check_assumptions(val, **symb.assumptions0)
                        if test:
                            continue
                        if test is False:
                            break
                        a_None = True
                    else:
                        no_False.append(sol)
                        if a_None:
                            got_None.append(sol)
            else:  # list of expressions
                for sol in solution:
                    test = check_assumptions(sol, **symbols[0].assumptions0)
                    if test is False:
                        continue
                    no_False.append(sol)
                    if test is None:
                        got_None.append(sol)

        elif type(solution) is dict:
            a_None = False
            for symb, val in solution.items():
                test = check_assumptions(val, **symb.assumptions0)
                if test:
                    continue
                if test is False:
                    no_False = None
                    break
                a_None = True
            else:
                no_False = solution
                if a_None:
                    got_None.append(solution)

        elif isinstance(solution, (Relational, And, Or)):
            assert len(symbols) == 1
            if warning and symbols[0].assumptions0:
                warnings.warn(filldedent("""
                    \tWarning: assumptions about variable '%s' are
                    not handled currently.""" % symbols[0]))
            # TODO: check also variable assumptions for inequalities

        else:
            raise TypeError('Unrecognized solution')  # improve the checker

        solution = no_False
        if warning and got_None:
            warnings.warn(filldedent("""
                \tWarning: assumptions concerning following solution(s)
                can't be checked:""" + '\n\t' +
                ', '.join(str(s) for s in got_None)))

    #
    # done
    ###########################################################################

    as_dict = flags.get('dict', False)
    as_set = flags.get('set', False)

    if not as_set and isinstance(solution, list):
        # Make sure that a list of solutions is ordered in a canonical way.
        solution.sort(key=default_sort_key)

    if not as_dict and not as_set:
        return solution or []

    # return a list of mappings or []
    if not solution:
        solution = []
    else:
        if isinstance(solution, dict):
            solution = [solution]
        elif iterable(solution[0]):
            solution = [dict(list(zip(symbols, s))) for s in solution]
        elif isinstance(solution[0], dict):
            pass
        else:
            assert len(symbols) == 1
            solution = [{symbols[0]: s} for s in solution]
    if as_dict:
        return solution
    assert as_set
    if not solution:
        return [], set()
    k = sorted(list(solution[0].keys()), key=lambda i: i.sort_key())
    return k, set([tuple([s[ki] for ki in k]) for s in solution])
