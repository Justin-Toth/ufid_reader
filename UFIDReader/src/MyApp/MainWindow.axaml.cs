using Avalonia.Controls;
using Avalonia.Threading;
using System;

namespace MyAvaloniaApp;

public partial class MainWindow : Window
{
    private readonly TextBlock _clockText;

    public MainWindow()
    {
        InitializeComponent();

        // Find the clock TextBlock
        _clockText = this.FindControl<TextBlock>("ClockText");

        // Start updating the clock
        StartClock();
    }

    private void StartClock()
    {
        // Update clock every second
        DispatcherTimer timer = new DispatcherTimer
        {
            Interval = TimeSpan.FromSeconds(1)
        };

        timer.Tick += (sender, e) =>
        {
            _clockText.Text = DateTime.Now.ToString("hh:mm:ss tt"); // Grab time from system
        };

        timer.Start();
    }
}
