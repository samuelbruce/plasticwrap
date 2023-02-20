
import plasticwrap

def main():
    with plasticwrap.PlasticWrap() as plastic:
        lines = plastic.get_revision_contents(repname="xcad", revid=96560)
        with open("test.tab", "w") as f:
            f.writelines([line.decode("utf-8")+"\n" for line in lines])

if __name__ == "__main__":
    main()

