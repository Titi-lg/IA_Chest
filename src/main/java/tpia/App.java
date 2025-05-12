package tpia;

import tpia.model.Plateau;

/**
 * Hello world!
 *
 */
public class App 
{
    public static void main( String[] args )
    {

        Plateau map = new Plateau(8, 8);
        map.initMap();
        map.setPiece(0, 0, 260);
        System.out.println(map);
    }
}
