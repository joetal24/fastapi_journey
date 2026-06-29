import time

fake_plots = {
    "VOL001": {"owner": "Talemwa Joel", "location": "Kampala", "size": 0.5, "price": 150_000_000},
    "VOL002": {"owner": "Jane Nakamya", "location": "Wakiso", "size": 1.0, "price": 200_000_000},
    "VOL003": {"owner": "Moses Sserwanga", "location": "Mukono", "size": 2.0, "price": 350_000_000},
    "VOL004": {"owner": "Sarah Nambi", "location": "Entebbe", "size": 0.75, "price": 180_000_000},
}

def get_plot_from_db(plot_id):
    time.sleep(0.5)
    return fake_plots.get(plot_id)

def update_plot_in_db(plot_id, new_data):
    if plot_id in fake_plots:
        fake_plots[plot_id].update(new_data)
        return fake_plots[plot_id]
    return None


