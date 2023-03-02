def smart_attack(P, Q):
    '''Returns k such that Q = kP, when E is anomalous.'''
    xP, yP = map(int, P.xy())
    xQ, yQ = map(int, Q.xy())

    E = P.curve().short_weierstrass_model()
    _, _, _, a, b = map(int, E.ainvs())

    K = Qp(E.base_field().characteristic(), 2)
    E_ = EllipticCurve(K, [a, b])
    _, _, _, A, B = E_.ainvs()

    xP_ = K(xP)
    yP_ = sqrt(xP_^3 + A*xP_ + B)
    P_  = E_(xP_, yP_ if yP_.expansion(0) == yP else -yP_)

    xQ_ = K(xQ)
    yQ_ = sqrt(xQ_^3 + A*xQ_ + B)
    Q_  = E_(xQ_, yQ_ if yQ_.expansion(0) == yQ else -yQ_)

    lP = E_.formal_group().log()(-(p*P_)[0]/(p*P_)[1])/p
    lQ = E_.formal_group().log()(-(p*Q_)[0]/(p*Q_)[1])/p

    k = (lQ/lP).expansion(0)
    return k