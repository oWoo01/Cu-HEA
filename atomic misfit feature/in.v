units		metal
atom_style	atomic
boundary	p p p

variable	ndelta equal 450
read_data	data/data.${a}	

pair_style	eam/alloy
pair_coeff	* * ../p_func/FeNiCrCoCu-heafixed.setfl Fe Ni Cr Co Cu

mass		1 55.847 # Fe
mass		2 58.693 # Ni
mass		3 51.960 # Cr
mass		4 58.933 # Co
mass		5 63.546 # Cu

# ------compute atomic volume-------
compute		vor all voronoi/atom
compute		avgvol all reduce ave c_vor[1]
variable	avgvol equal c_avgvol
variable	voltot equal vol
dump		voro_dump all custom 100 txt/voro_${a}.dump id type x y z c_vor[1]
dump_modify	voro_dump element Fe Ni Cr Co Cu sort id
run		0
undump		voro_dump

variable	avggrad equal (3*${avgvol}/(4*3.1415926535))^(1/3)
print		"${a} ${voltot} ${avggrad}" append txt/aveV.txt screen no

# --------compute compress modulus--------
compute		peatom all pe/atom
compute		petot all pe
variable	V0 equal vol
variable	P0 equal 0

dump		compress_dump all custom 1000000 txt/compress/compress_${a}_*.dump id type x y z c_vor[1] c_peatom
dump_modify	compress_dump element Fe Ni Cr Co Cu sort id

thermo_style	custom step vol pe
thermo 		100
variable	Vnow equal vol
variable	V1 equal vol/${V0}
variable	Vt equal v_V1
variable	Pe equal c_petot
# fix 		compress_data all print 10 "${Vt} ${Pe}" append txt/compress_${a}.txt screen no

label		loop
variable	loopa loop ${ndelta}

fix 		1 all deform 1 x delta 0.01 -0.01 &
		y delta 0.01 -0.01 &
		z delta 0.01 -0.01 units box remap x

run		1
minimize	1e-15 1e-15 100000 100000
print		"${loopa} ${Vt} ${Pe}" append txt/compress_${a}.txt screen no
next		loopa
jump		SELF loop



