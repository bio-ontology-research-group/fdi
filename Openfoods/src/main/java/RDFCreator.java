import java.io.*;
import java.nio.*;
import java.nio.file.*;
import java.util.*;
import org.apache.jena.rdf.model.*;

public class RDFCreator {

    Map<String, String> foodId;
    String rootURI = "http://cbrc.kaust.edu.sa/ai/fdi/";
    String pubchemURI = "http://rdf.ncbi.nlm.nih.gov/pubchem/compound/CID";
    String chebiURI = "http://purl.obolibrary.org/obo/";
    String drugBankURI = "http://www.drugbank.ca/drugs/";

    public RDFCreator(Properties props) {
        this.foodId = new HashMap<String, String>();
    }

    public String getFoodId(String foodName) {
        if (!this.foodId.containsKey(foodName)) {
            int id = this.foodId.size();
            String foodId = "FDI_" + String.format("%07d", id);
            this.foodId.put(foodName, foodId);
            return foodId;
        }
        return this.foodId.get(foodName);
    }

    public Map<String, List<String> > loadFoods() throws Exception {
        Map<String, List<String> > foods = new HashMap<String, List<String> >();
        // Loading list of ingreadients from openfoodfacts database
        String filePath = "data/ingredients.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String foodName = items[1];
                String ingName = items[2];
                if (!foods.containsKey(foodName)) {
                    foods.put(foodName, new ArrayList<String>());
                }
                foods.get(foodName).add(ingName);
            }
        }
        // Loading ingredients from openrecipe database recipes
        filePath = "data/recipe_ingredients.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String foodName = items[0];
                String ingName = items[1];
                if (!foods.containsKey(foodName)) {
                    foods.put(foodName, new ArrayList<String>());
                }
                foods.get(foodName).add(ingName);
            }
        }

        return foods;
    }

    public Map<String, List<String> > loadChemicals() throws Exception {
        Map<String, List<String> > map = new HashMap<String, List<String> >();
        String filePath = "data/ingredients-chebi-uniq.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String ingName = items[0];
                String[] chebi = items[1].split("\\|");
                if (Double.parseDouble(chebi[2]) >= 0.1) {
                    if (!map.containsKey(ingName)) {
                        map.put(ingName, new ArrayList<String>());
                    }
                    map.get(ingName).add(chebi[0].replaceAll(":", "_"));
                }

            }
        }
        filePath = "data/ingredients-pubchem-uniq.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String ingName = items[0];
                String pub = items[1].split("\\|")[0];
                if (!map.containsKey(ingName)) {
                    map.put(ingName, new ArrayList<String>());
                }
                map.get(ingName).add(pub);
            }
        }
        return map;
    }

    public Map<String, Set<String> > loadDrugs() throws Exception {
        Map<String, Set<String> > map = new HashMap<String, Set<String> >();
        String filePath = "data/chebi-drugbank.txt";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split(" ", -1);
                String chebiId = items[0].replaceAll(":", "_");
                String dbId = items[1];
                if (!map.containsKey(chebiId)) {
                    map.put(chebiId, new HashSet<String>());
                }
                map.get(chebiId).add(dbId);
            }
        }
        filePath = "data/pubchem_drugbank_chebi.tsv";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String pub = items[0];
                String[] dbIds = items[1].split("\\|");
                String[] chebiIds = items[2].split("\\|");

                if (!map.containsKey(pub)) {
                    map.put(pub, new HashSet<String>());
                }
                for (String dbId: dbIds) {
                    map.get(pub).add(dbId);
                }
                if (!chebiIds[0].equals(".")) {
                    for (String chebiId: chebiIds) {
                        chebiId = chebiId.replaceAll(":", "_");
                        if (!map.containsKey(chebiId)) {
                            map.put(chebiId, new HashSet<String>());
                        }
                        for (String dbId: dbIds) {
                            map.get(chebiId).add(dbId);
                        }
                    }
                }

            }
        }
        return map;
    }

    public Map<String, Set<String> > loadDrugInteractions() throws Exception {
        Map<String, Set<String> > map = new HashMap<String, Set<String> >();
        String filePath = "data/drug-drug-interactions.tsv";
        try(BufferedReader br = Files.newBufferedReader(Paths.get(filePath))) {
            String line;
            while((line = br.readLine()) != null) {
                String[] items = line.split("\t", -1);
                String dbId1 = items[0];
                String dbId2 = items[1];
                if (!map.containsKey(dbId1)) {
                    map.put(dbId1, new HashSet<String>());
                }
                map.get(dbId1).add(dbId2);
            }
        }

        return map;
    }



    public void create() throws Exception {
        Model model = ModelFactory.createDefaultModel();
        Map<String, List<String> > foodMap = loadFoods();
        for (String foodName: foodMap.keySet()) {
            String foodId = this.getFoodId(foodName);
            Resource food = model.createResource(this.rootURI + foodId, FDI.Food);
            food.addProperty(FDI.NAME, foodName);
            for (String ingName: foodMap.get(foodName)) {
                String ingId = this.getFoodId(ingName);
                Resource ing = model.createResource(this.rootURI + ingId, FDI.Food);
                ing.addProperty(FDI.NAME, ingName);
                food.addProperty(FDI.hasIngredient, ing);
            }
        }

        Map<String, List<String> > chemMap = this.loadChemicals();
        for (String ingName: chemMap.keySet()) {
            String ingId = this.getFoodId(ingName);
            Resource ing = model.createResource(this.rootURI + ingId, FDI.Food);
            for (String chemId: chemMap.get(ingName)) {
                String chemURI = "";
                if (chemId.startsWith("CHEBI")) {
                    chemURI = this.chebiURI + chemId;
                } else {
                    chemURI = this.pubchemURI + chemId;
                }
                Resource chem = model.createResource(chemURI, FDI.ChemicalCompound);
                ing.addProperty(FDI.hasChemical, chem);
            }
        }

        Map<String, Set<String> > drugMap = this.loadDrugs();
        for (String chemId: drugMap.keySet()) {
            String chemURI = "";
            if (chemId.startsWith("CHEBI")) {
                chemURI = this.chebiURI;
            } else {
                chemURI = this.pubchemURI;
            }
            Resource chem = model.createResource(chemURI + chemId, FDI.ChemicalCompound);
            for (String dbId: drugMap.get(chemId)) {
                Resource drug = model.createResource(drugBankURI + dbId, FDI.Drug);
                chem.addProperty(FDI.canActAs, drug);
            }
        }

        Map<String, Set<String> > intMap = this.loadDrugInteractions();
        for (String dbId: intMap.keySet()) {
            Resource drug1 = model.createResource(this.drugBankURI + dbId, FDI.Drug);
            for (String dbId2: intMap.get(dbId)) {
                Resource drug2 = model.createResource(this.drugBankURI + dbId2, FDI.Drug);
                drug1.addProperty(FDI.interactsWith, drug2);
            }
        }
        PrintWriter out = new PrintWriter("data/fdi.rdf");
        model.write(out, "RDF/XML");
    }
}
