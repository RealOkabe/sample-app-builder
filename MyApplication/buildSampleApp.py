import requests
import xml.etree.ElementTree as ET
import os

API_URL = "https://search.maven.org/remotecontent?filepath="

def downloadAar(groupId, artifactId, version, extension="aar"):
    """Downloads an AAR artifact from Maven Central."""
    fileName = f"{artifactId}-{version}.{extension}"
    url = f"{API_URL}{groupId.replace('.', '/')}/{artifactId}/{version}/{fileName}"
    response = requests.get(url)
    if '404 Not Found' in response.text:
        downloadAar(groupId, artifactId, version, 'jar')
    else:
        with open(f"app/libs/{fileName}", "wb") as file:
            file.write(response.content)

def extractAndDownloadDependencies(pomUrl):
    """Extracts dependencies from a POM file and downloads them."""
    response = requests.get(pomUrl)
    pomParsed = ET.fromstring(response.text)

    for dependency in pomParsed.findall('.//{*}dependency'):
        groupId = dependency.find('{*}groupId').text
        artifactId = dependency.find('{*}artifactId').text
        version = dependency.find('{*}version').text
        downloadAar(groupId, artifactId, version)

def addDependencyToGradle(dependencyCode):
    """Adds a dependency line to the app/build.gradle file."""
    with open('app/build.gradle', 'r+') as gradleFile:
        fileLines = gradleFile.readlines()
        fileLines[-1] = f'    {dependencyCode}\n' + '}'
        gradleFile.seek(0)
        gradleFile.truncate(0)
        gradleFile.writelines(fileLines)

if __name__ == "__main__":
    downloadMethod = input("Choose download method:\n1. Download dependencies from Maven)\n2. Manually add dependency code (for adding individual dependencies)\nEnter choice (1 or 2): ")

    if downloadMethod == "1":
        sdkDetails = input("Please enter the SDK Details in the format <group id>:<artifact id> (e.g., com.criteo.publisher:criteo-publisher-sdk):\n")
        sdkVersion = input("Please enter the SDK version (e.g., 6.0.0):\n")
        groupId, artifactId = sdkDetails.split(':')
        # Download the main SDK AAR
        downloadAar(groupId, artifactId, sdkVersion)

        # Construct the POM URL and download/parse it
        pomUrl = f"{API_URL}{groupId.replace('.', '/')}/{artifactId}/{sdkVersion}/{artifactId}-{sdkVersion}.pom"
        extractAndDownloadDependencies(pomUrl)
    elif downloadMethod == "2":
        dependencyCode = input("Please enter the dependency addition code: Example: implementation '<group id:artifact id:version>'\n")
        addDependencyToGradle(dependencyCode)
    else:
        print("Invalid choice. Please enter 1 or 2.")

    # Build the project 
    os.system("./gradlew build && ./gradlew assembleRelease") 