package tpia.model;
public enum Piece {
        EMPTY(1),
        WHITE(2),
        BLACK(4),

        PION(8),
        TOUR(16),
        FOU(32),
        CAVALIER(64),
        REINE(128),
        ROI(256);

        private final int value;

        Piece(int value) {
            this.value = value;
        }

        public int getValue() {
            return value;
        }
    }