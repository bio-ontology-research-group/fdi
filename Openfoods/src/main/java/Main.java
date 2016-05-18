import java.io.*;
import java.util.*;

public class Main {

    public static final String PROJECT_PROPERTIES = "project.properties";
    Properties props;
    IngredientParser ingredientParser;
    Annotations annotations;
    RDFCreator rdfCreator;

    public Main() throws Exception {
        this.props = this.getProperties();
        this.ingredientParser = new IngredientParser(this.props);
        this.annotations = new Annotations(this.props);
        this.rdfCreator = new RDFCreator(this.props);
    }

    public Properties getProperties() throws Exception {
        if (this.props != null) {
            return this.props;
        }
        ClassLoader loader = Thread.currentThread().getContextClassLoader();
        Properties props = new Properties();
        InputStream is = loader.getResourceAsStream(PROJECT_PROPERTIES);
        props.load(is);
        return props;
    }

    public void run(String[] args) throws Exception {
        // this.ingredientParser.parseOpenFoods();
        // this.annotations.getChebiAnnotations();
        // this.annotations.getDrugbankAnnotations();
        // this.annotations.getHighScoreDB();
        // this.annotations.getPubchemAnnotations();
        // this.annotations.mapPubchemDB();
        // this.annotations.foodDrugDrugInteractions();
        // this.annotations.validation();
        this.rdfCreator.create();
    }


    public static void main(String[] args) throws Exception {
        new Main().run(args);
    }
}
