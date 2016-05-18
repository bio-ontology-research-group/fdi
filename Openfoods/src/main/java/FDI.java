import org.apache.jena.rdf.model.* ;

/** FDI vocabulary class for namespace http://cbrc.kaust.edu.sa/ai/fdi#
 */
public class FDI {

    /**
     * The namespace of the vocabulary as a string
     */
    public static final String uri ="http://cbrc.kaust.edu.sa/ai/fdi#";

    /** returns the URI for this schema
     * @return the URI for this schema
     */
    public static String getURI() {
          return uri;
    }

    private static final Model m = ModelFactory.createDefaultModel();

    public static final Resource Food = m.createResource(uri + "Food");
    public static final Resource ChemicalCompound = m.createResource(uri + "ChemicalCompound" );
    public static final Resource Drug = m.createResource(uri + "Drug");
    public static final Property canActAs = m.createProperty(uri, "canActAs");
    public static final Property hasChemical = m.createProperty(uri, "hasChemical");
    public static final Property hasIngredient = m.createProperty(uri, "hasIngredient");
    public static final Property interactsWith = m.createProperty(uri, "interactsWith");
    public static final Property isIngredientOf = m.createProperty(uri, "isIngredientOf");
    public static final Property NAME = m.createProperty(uri, "NAME" );
}
