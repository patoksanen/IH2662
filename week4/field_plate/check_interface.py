"""Analytical two-dielectric capacitor test of the field-plate interface helpers."""
from pathlib import Path
import json
import numpy as np
import devsim as ds
import devsim.umfpack.umfshim
from devsim.python_packages.simple_physics import CreateOxidePotentialOnly, CreateOxideContact, CreateSiliconOxideInterface

def main():
    device='capacitor_check'; mesh='capacitor_check'
    ds.create_1d_mesh(mesh=mesh)
    for pos,tag in [(0,'top'),(1e-4,'interface'),(3e-4,'bottom')]:
        ds.add_1d_mesh_line(mesh=mesh,pos=pos,ps=1e-5,tag=tag)
    ds.add_1d_region(mesh=mesh,material='Oxide',region='Oxide',tag1='top',tag2='interface')
    ds.add_1d_region(mesh=mesh,material='Silicon',region='Silicon',tag1='interface',tag2='bottom')
    ds.add_1d_contact(mesh=mesh,name='top',tag='top',material='metal')
    ds.add_1d_contact(mesh=mesh,name='bottom',tag='bottom',material='metal')
    ds.add_1d_interface(mesh=mesh,name='dielectric_interface',tag='interface')
    ds.finalize_mesh(mesh=mesh); ds.create_device(mesh=mesh,device=device)
    eps={'Oxide':3.9*8.8541878128e-14,'Silicon':11.7*8.8541878128e-14}
    for region in eps:
        ds.set_parameter(device=device,region=region,name='Permittivity',value=eps[region])
        CreateOxidePotentialOnly(device,region)
    ds.set_parameter(device=device,name='bottom_bias',value=0)
    ds.set_parameter(device=device,name='top_bias',value=0)
    CreateOxideContact(device,'Oxide','top'); CreateOxideContact(device,'Silicon','bottom')
    CreateSiliconOxideInterface(device,'dielectric_interface')
    checks=[]
    for bias in (1.,2.):
        ds.set_parameter(device=device,name='top_bias',value=bias)
        ds.solve(type='dc',absolute_error=1e-14,relative_error=1e-12,maximum_iterations=20)
        displacement=bias/(1e-4/eps['Oxide']+2e-4/eps['Silicon'])
        errors={}
        for region in eps:
            actual=np.array(ds.get_edge_model_values(device=device,region=region,name='ElectricField'))
            expected=displacement/eps[region]
            assert np.allclose(actual,expected,rtol=1e-9,atol=1e-8),(region,actual,expected)
            errors[region]=float(np.max(np.abs(actual-expected))/abs(expected))
        interface=np.array(ds.get_interface_model_values(device=device,interface='dielectric_interface',name='continuousPotential'))
        assert np.max(np.abs(interface))<1e-10
        charges=[ds.get_contact_charge(device=device,contact=c,equation='PotentialEquation') for c in ('top','bottom')]
        assert abs(sum(charges))<abs(displacement)*1e-9
        checks.append(dict(bias_V=bias,field_relative_errors=errors,interface_mismatch_V=float(np.max(np.abs(interface)))))
    report=dict(status='PASS: series-capacitor fields, displacement balance, potential continuity at 1 and 2 V',checks=checks)
    out=Path(__file__).resolve().parent/'diagnostics'; out.mkdir(exist_ok=True)
    (out/'capacitor_checks.json').write_text(json.dumps(report,indent=2))
    print(json.dumps(report,indent=2))
    print('Contact residual API:',hasattr(ds,'get_contact_node_model_values'))

if __name__=='__main__': main()
