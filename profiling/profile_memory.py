from memory_profiler import profile

from main import main


@profile
def run() -> None:
    main()


if __name__ == "__main__":
    run()
