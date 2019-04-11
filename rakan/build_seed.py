import supers

supers.build_supers('WA2.dnx', 300, 10, 'super_map.csv', 'supers.dnx')
supers.translate('supers.dnx', 'super_map.csv', 'WA2.dnx', 'wa_seed.dnx')

r = supers.Rakan()
r.read_nx('wa_seed.dnx')
r.show("dists.png")