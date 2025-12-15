from photons import App, utils

x0 = 57.518 # mm
y0 = 6.660  # mm
width = 8 # mm
step = 1 # mm
delta_xy = [(0, 0), (-0.1, -0.1), (0.1, -0.1), (0.1, 0.1), (-0.1, 0.1)] # mm
sleep = 2 # seconds

app = App()

x_values = utils.array_central(
    centre=x0,
    width=width,
    step=step,
)
y_values = utils.array_central(
    centre=y0,
    width=width,
    step=step,
)

def fetch():
    app.sleep(sleep)
    dmm_mon.initiate()
    dmm_dut.initiate()
    mon_data = dmm_mon.fetch()
    dut_data = dmm_dut.fetch()
    return mon_data.mean, mon_data.stdom, dut_data.mean, dut_data.stdom


shutter, dmm_dut, dmm_mon, stage_x, stage_y = app.connect_equipment('shutter-mg', 'dmm-dut', 'dmm-mon', 'stage-x', 'stage-y')
mon_settings = dmm_mon.configure()
dut_settings = dmm_dut.configure()
with app.create_writer('photometer_spatial_scan') as writer:

    for (dx, dy) in delta_xy:
        dataset_name = f"{dx,dy}"
        writer.initialize('x', 'y', 'mon', 'mon_stdom', 'photometer', 'photometer_stdom', name=dataset_name)

        shutter.close()
        dark = fetch()
        writer.update_metadata(dataset_name, dark=dark)
        shutter.open()

        for y in y_values:
            stage_y.set_position(y + dy)
            for x in x_values:
                stage_x.set_position(x + dx)
                data = fetch()
                writer.append(*(stage_x.get_position(), stage_y.get_position(), *data), name=dataset_name)

    shutter.close()
    dark_end = fetch()
    writer.add_metadata(dark_final=dark_end, x0=x0, y0=y0, width=width, step=step)

app.disconnect_equipment()
