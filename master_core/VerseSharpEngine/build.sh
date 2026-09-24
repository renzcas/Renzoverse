#!/bin/bash

echo "Building VerseSharpEngine..."
dotnet build VerseSharpEngine/VerseSharpEngine.csproj

echo "Running VerseSharpEngine..."
dotnet run --project VerseSharpEngine/VerseSharpEngine.csproj

