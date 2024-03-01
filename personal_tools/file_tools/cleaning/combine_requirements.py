from pathlib import Path

if __name__ == "__main__":
    requirement_filepaths = list(Path(".").rglob("requirements.txt"))
    requirement_filepaths = sorted(requirement_filepaths)

    with open("./requirements.txt", "w") as file:
        for filepath in requirement_filepaths:
            with open(filepath, "r") as f:
                file.write("# " + str(filepath) + "\n")
                file.write(f.read())
                file.write("\n")

    print("Combined requirements.txt")
