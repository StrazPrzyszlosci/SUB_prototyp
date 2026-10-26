"""Porównanie tej samej przedniej objętości powietrza z modułami P20A.

Znany bilans części; niezaprojektowane szyny/śruby nadal wymagają objętości.
"""
import copy
import numpy as np
from scipy.optimize import brentq
from geometria_wkladow_P20A import obstacles,liner_envelope_volume


def matched_geometry(base,cfg,module_count,thickness,lining='AIR_ONLY',driver_l=4.,host='FIXED'):
    W,D,H=base['inside_width_depth_height_m'];area=W*H
    hard=obstacles(base,1);fixed=sum(b.volume for b in hard)
    liner_full=liner_envelope_volume(base,hard)
    factor=0. if lining=='AIR_ONLY' else 1-base['lining_geometric_porosity_assumed']
    module_v=float(np.prod(base['selected_comparison_outer_width_length_height_m']))
    target=area*D-fixed-driver_l*.001-module_count*module_v-factor*liner_full
    lower=max(b.hi[1] for b in hard)+base['geometric_clearance_m_assumed']
    def geometry_at(y):
        active=copy.deepcopy(base);active['inside_width_depth_height_m']=[W,y,H]
        volume_liner=liner_envelope_volume(active,hard)
        return area*y-fixed-driver_l*.001-factor*volume_liner,volume_liner
    if module_count==0:position=D
    else:position=brentq(lambda y:geometry_at(y)[0]-target,lower,D,xtol=1e-13)
    actual,liner=geometry_at(position);assert abs(actual-target)<1e-12
    inside_depth=D if host=='FIXED' else D+thickness+cfg['rear_parking_gap_m_assumed']
    back_length=inside_depth-position-thickness
    feasible=back_length>=cfg['rear_parking_gap_m_assumed']-1e-12
    gap=cfg['panel_edge_clearance_m_assumed'];panel_a=W-2*gap;panel_b=H-2*gap
    diameters=base['nominal_opening_diameters_m']
    # Każda ciągła droga środka płyty przez otwór przecina jego płaszczyznę.
    # W tej chwili środkowy wpisany dysk ma w przekroju średnicę >=min(a,b).
    necessary_diameter=min(panel_a,panel_b)
    tool_r=.005;dx,dz=cfg['support_offset_from_center_m']
    tool_pass=all(np.hypot(dx,dz)+tool_r<d/2 for d in diameters)
    return dict(module_count=module_count,thickness_m=thickness,lining=lining,driver_displacement_l_stress_axis=driver_l,host=host,
        matched_position_from_inner_front_m=float(position),inside_depth_m=inside_depth,
        matched_active_air_l=actual*1000,ideal_target_air_l=target*1000,
        front_liner_envelope_l=liner*1000,module_reference_liner_envelope_l=liner_full*1000,
        front_liner_dry_mass_kg=base['lining_dry_density_kg_m3_assumed']*liner if factor else 0.,
        rear_geometric_air_l=max(0.,area*back_length*1000),rear_length_m=back_length,
        feasible_with_rear_gap=bool(feasible),required_front_air_match_error_l=(actual-target)*1000,
        whole_plate_necessary_aperture_m=necessary_diameter,
        whole_rigid_plate_aperture_possible=bool(max(diameters)>=necessary_diameter),
        four_tool_axes_fit_nominal_apertures=bool(tool_pass),
        tool_required_axial_reach_m=position+base['host_wall_thickness_m'],
        extra_depth_m=inside_depth-D,
        extra_side_wall_mdf_mass_kg=base['mdf_density_kg_m3_assumed']*((W+2*base['host_wall_thickness_m'])*(H+2*base['host_wall_thickness_m'])-area)*(inside_depth-D),
        scope='Front lining is geometry-dependent; thermal comparison is a package comparison, not equal quantity of fibre. Hardware volume excluded pending design.')
