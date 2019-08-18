import oommfc as oc
import oommfc.util as ou
from .driver import Driver


class TimeDriver(Driver):
    _allowed_kwargs = ['evolver',
                       'stopping_dm_dt',
                       'stage_iteration_limit',
                       'total_iteration_limit',
                       'stage_count_check',
                       'checkpoint_file',
                       'checkpoint_interval',
                       'checkpoint_disposal',
                       'start_iteration',
                       'start_stage',
                       'start_stage_iteration',
                       'start_stage_start_time',
                       'start_stage_elapsed_time',
                       'start_last_timestep',
                       'normalize_aveM_output',
                       'report_max_spin_angle',
                       'report_wall_time']

    def _script(self, system, **kwargs):
        # Save initial magnetisation.
        m0mif, m0name, Msname = ou.setup_m0(system.m, 'm0')
        mif = m0mif

        # Evolver
        if not hasattr(self, 'evolver'):
            self.evolver = oc.RungeKuttaEvolver()

        # Extract dynamics equation parameters.
        gamma, alpha = None, None
        for term in system.dynamics.terms:
            if isinstance(term, oc.Precession):
                gamma = term.gamma
            if isinstance(term, oc.Damping):
                alpha = term.alpha

        if gamma is not None:
            self.evolver.gamma_G = gamma
        else:
            self.evolver.do_precess = 0  # do_precess default value is 1

        if alpha is not None:
            self.evolver.alpha = alpha
        else:
            self.evolver.alpha = 0

        # Evolver script
        if isinstance(self.evolver, (oc.EulerEvolver, oc.RungeKuttaEvolver)):
            mif += self.evolver._script
        else:
            msg = 'Evolver must be either EulerEvolver or RungeKuttaEvolver.'
            raise ValueError(msg)

        # For deriving, a small timestep is chosen.
        if 'derive' in kwargs:
            t, n = 1e-25, 1
            self.total_iteration_limit = 1
        else:
            t, n = kwargs['t'], kwargs['n']

        # TimeDriver
        mif += '# TimeDriver\n'
        mif += 'Specify Oxs_TimeDriver {\n'
        mif += '  evolver :evolver\n'
        mif += '  mesh :mesh\n'
        mif += f'  Ms :{Msname}\n'
        mif += f'  m0 :{m0name}\n'
        mif += f'  stopping_time {t/n}\n'
        mif += f'  stage_count {n}\n'
        # Other parameters for TimeDriver
        for kwarg in self._allowed_kwargs:
            if hasattr(self, kwarg) and kwarg != 'evolver':
                mif += f'  {kwarg} {getattr(self, kwarg)}\n'
        mif += '}\n\n'

        # Saving results
        mif += 'Destination table mmArchive\n'
        mif += 'Destination mags mmArchive\n'
        mif += 'Destination archive mmArchive\n\n'

        if 'derive' in kwargs:
            if 'ield' in kwargs['derive'] or 'density' in kwargs['derive']:
                mif += ('Schedule \"{}\" archive '
                        'Step 1'.format(kwargs['derive']))
            else:
                mif += 'Schedule DataTable table Stage 1\n'
        else:
            mif += 'Schedule DataTable table Stage 1\n'
            mif += 'Schedule Oxs_TimeDriver::Magnetization mags Stage 1'

        return mif

    def _checkargs(self, **kwargs):
        if 'derive' not in kwargs:
            if kwargs['t'] <= 0:
                msg = 'Positive simulation time expected (t>0).'
                raise ValueError(msg)
            if kwargs['n'] <= 0 or not isinstance(kwargs['n'], int):
                msg = 'Positive integer number of steps expected (n>0)'
                raise ValueError(msg)


"""
mif = '# SpinTransferTorqueEvolver\n'
            mif += 'Specify Anv_SpinTEvolve {\n'
            mif += '  do_precess 1\n'
            mif += '  gamma_G {}\n'.format(gamma)
            mif += '  alpha {}\n'.format(alpha)
            mif += '  method rkf54s\n'
            mif += '  u {\n'
            mif += '    Oxs_UniformScalarField {\n'
            mif += '      value {}\n'.format(u[0])
            mif += '    }\n'
            mif += '  }\n'
            mif += '  beta {}\n'.format(beta)
            mif += '}\n\n'
            evolver = 'Anv_SpinTEvolve'


Specify Anv_SpinTEvolve {
  do_precess 1
  gamma_LL 2.21e5
  method rkf54s
  alpha 0.005
  fixed_spins {
  	atlas fixed
  }
  u {Oxs_UniformScalarField {
   value 100
	}}
  beta 0.04
  	
}
"""
