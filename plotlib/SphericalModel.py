class SphericalModel:
    def __init__( self, P, hs, bw ):
        self.sv = SV( P, hs, bw )
        self.C0 = C( P, hs[0], bw )
    def fit( self ):
        C0 = self.C0
        def spherical( h, a ):
            try:
                _ = iter( h )
                h = np.asarray( h )
                return map( spherical, h, [a]*h.size )
            except TypeError:
                a = float( a )
                if h <= a:
                    return C0*( 1.5*h/a - 0.5*( h/a )**3.0 )
                else:
                    return C0
        x, y = self.sv
        self.param = opt( spherical, self.sv[0], self.sv[1] )
        self.model = lambda h, a=self.param: spherical( h, a )
        self.covfct = lambda h, a=self.param: C0 - spherical( h, a )
         
        return self