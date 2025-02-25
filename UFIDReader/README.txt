AVALONIA README

In order to run avalonia your system must have .NET downloaded
1. Check if you have avalonia .NET SDK intalled:
    dotnet --version

2. Verify version is 9.0:
    dotnet --info

IF NOT INSTALLED:
    Download from Microsoft's .NET Download Page:  https://dotnet.microsoft.com/en-us/download/dotnet/9.0

4. Navigate to MyApp directory:
    cd ./ufid_reader/UFIDReader/src/MyApp
    
3. Once installed run:
    dotnet restore

4. Run the application
    dotnet run

KEY NOTES:
Must be in UFIDReader dir in order to succesfully run GUI
EX:
    cd ./ufid_reader/UFIDReader/src/MyApp
    dotnet restore
    dotnet run

