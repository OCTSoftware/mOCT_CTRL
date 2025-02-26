import customtkinter as ctk

# Event handlers
def on_mouse_down(event):
    print("Mouse Down event triggered")

def on_mouse_up(event):
    print("Mouse Up event triggered")

def on_slider_move(event):
    # Get the current slider value and print it
    print(f"Slider value: {slider.get()}")

# Set up the application window
root = ctk.CTk()

# Create the slider
slider = ctk.CTkSlider(root, from_=0, to=100, width=200)
slider.pack(padx=20, pady=20)

# Bind events
slider.bind("<ButtonPress-1>", on_mouse_down)  # Mouse down event
slider.bind("<ButtonRelease-1>", on_mouse_up)  # Mouse up event
slider.bind("<B1-Motion>", on_slider_move)  # Continuous update while moving the slider

# Start the GUI loop
root.mainloop()
