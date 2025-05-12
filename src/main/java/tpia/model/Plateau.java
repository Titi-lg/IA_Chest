package tpia.model;

import java.util.ArrayList;

public class Plateau {
    private final ArrayList<Integer> Map;
    private final int width;
    private final int height;

    public Plateau(int width, int height) {
        this.width = width;
        this.height = height;
        Map = new ArrayList<Integer>(width*height);
    }

    public int getWidth() {
        return width;
    }

    public int getHeight() {
        return height;
    }

    public ArrayList<Integer> getMap() {
        return Map;
    }

    public void initMap() {
        for (int i = 0; i < width * height; i++) {
            Map.add(1);
        }
    }
    public void setPiece(int x, int y, Integer piece) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            Map.set(y * width + x, piece);
        } else {
            throw new IndexOutOfBoundsException("Coordinates out of bounds");
        }
    }
    public Integer getPiece(int x, int y) {
        if (x >= 0 && x < width && y >= 0 && y < height) {
            return Map.get(y * width + x);
        } else {
            throw new IndexOutOfBoundsException("Coordinates out of bounds");
        }
    }

    @Override
    public String toString() {
        return "Plateau{" +
                "Map=" + Map +
                ", width=" + width +
                ", height=" + height +
                '}';
    }
}
