import javax.sound.sampled.*;
import javax.swing.*;
import java.awt.*;
import java.awt.event.*;
import java.awt.geom.*;
import java.io.ByteArrayInputStream;
import java.util.ArrayList;
import java.util.List;
import java.util.Random;

/**
 * THE GREAT BAG BUSTER! (Polythene Bag Pop Game) - Java 2D Edition
 * Playable instantly with standard JDK (No installation needed!)
 */
public class BagBusterGame extends JPanel implements ActionListener, KeyListener, MouseListener {

    public static final int SCREEN_WIDTH = 900;
    public static final int SCREEN_HEIGHT = 600;

    // Palette
    private static final Color COLOR_BG_WALL = new Color(248, 241, 227);
    private static final Color COLOR_BG_WAINSCOT = new Color(222, 207, 182);
    private static final Color COLOR_WOOD_DARK = new Color(92, 58, 33);
    private static final Color COLOR_WOOD_LIGHT = new Color(168, 119, 74);
    private static final Color COLOR_WOOD_MID = new Color(133, 89, 52);
    private static final Color COLOR_CHALKBOARD = new Color(34, 76, 56);
    private static final Color COLOR_SHIRT = new Color(41, 98, 255);
    private static final Color COLOR_TIE = new Color(220, 38, 38);
    private static final Color COLOR_SKIN = new Color(255, 213, 179);
    private static final Color COLOR_CHEEKS_BLOW = new Color(255, 75, 75);
    private static final Color COLOR_HAIR = new Color(55, 35, 25);
    private static final Color COLOR_BAG_TINT = new Color(100, 210, 255);
    private static final Color COLOR_SWEAT = new Color(140, 220, 255);

    // State
    private double pressure = 0.0;
    private boolean isBlowing = false;
    private boolean gameWon = false;
    private int burstTimer = 0;
    private double totalTime = 0.0;
    private double shakeIntensity = 0.0;

    // Animations
    private int animTick = 0;
    private int blinkTimer = 180;
    private boolean isBlinking = false;
    private double clockAngle = 0.0;

    // Particles
    private final List<AirParticle> airParticles = new ArrayList<>();
    private final List<SweatDrop> sweatParticles = new ArrayList<>();
    private final List<PlasticShred> plasticShreds = new ArrayList<>();
    private final List<Confetti> confettiList = new ArrayList<>();

    // Button
    private final Rectangle btnRestartRect = new Rectangle(SCREEN_WIDTH / 2 - 120, SCREEN_HEIGHT / 2 + 130, 240, 50);
    private boolean btnHover = false;
    private boolean soundMuted = false;

    private final Random rand = new Random();

    public BagBusterGame() {
        setPreferredSize(new Dimension(SCREEN_WIDTH, SCREEN_HEIGHT));
        setBackground(COLOR_BG_WALL);
        setFocusable(true);
        addKeyListener(this);
        addMouseListener(this);
        addMouseMotionListener(new MouseMotionAdapter() {
            @Override
            public void mouseMoved(MouseEvent e) {
                btnHover = gameWon && btnRestartRect.contains(e.getPoint());
            }
        });

        // Initialize Confetti
        for (int i = 0; i < 110; i++) {
            confettiList.add(new Confetti(rand));
        }

        // 60 FPS Game Loop Timer
        Timer timer = new Timer(16, this);
        timer.start();
    }

    public void resetGame() {
        pressure = 0.0;
        isBlowing = false;
        gameWon = false;
        burstTimer = 0;
        totalTime = 0.0;
        shakeIntensity = 0.0;
        airParticles.clear();
        sweatParticles.clear();
        plasticShreds.clear();
    }

    // -------------------------------------------------------------
    // PROCEDURAL AUDIO SYNTHESIZER
    // -------------------------------------------------------------
    private void playTone(String type) {
        if (soundMuted) return;
        new Thread(() -> {
            try {
                int sampleRate = 44100;
                byte[] buffer;
                if ("blow".equals(type)) {
                    int duration = (int) (sampleRate * 0.45);
                    buffer = new byte[duration];
                    for (int i = 0; i < duration; i++) {
                        double t = (double) i / sampleRate;
                        double env = Math.sin(Math.PI * i / duration);
                        double noise = (rand.nextDouble() * 2.0 - 1.0) * 0.5;
                        double sine = Math.sin(2.0 * Math.PI * 140.0 * t) * 0.3;
                        buffer[i] = (byte) ((noise + sine) * env * 110);
                    }
                } else if ("pop".equals(type)) {
                    int duration = (int) (sampleRate * 0.4);
                    buffer = new byte[duration];
                    for (int i = 0; i < duration; i++) {
                        double t = (double) i / sampleRate;
                        double decay = Math.exp(-15.0 * t);
                        double freq = 550.0 * Math.exp(-25.0 * t) + 60.0;
                        double tone = Math.sin(2.0 * Math.PI * freq * t);
                        double noise = (rand.nextDouble() * 2.0 - 1.0) * Math.exp(-35.0 * t);
                        buffer[i] = (byte) ((tone + noise) * decay * 125);
                    }
                } else { // win
                    int duration = (int) (sampleRate * 0.8);
                    buffer = new byte[duration];
                    double[] notes = {523.25, 659.25, 783.99, 1046.50};
                    double noteLen = (double) duration / notes.length;
                    for (int i = 0; i < duration; i++) {
                        double t = (double) i / sampleRate;
                        int noteIdx = Math.min(notes.length - 1, (int) (i / noteLen));
                        double env = Math.sin(Math.PI * (i % noteLen) / noteLen);
                        double sample = Math.sin(2.0 * Math.PI * notes[noteIdx] * t) * env;
                        buffer[i] = (byte) (sample * 115);
                    }
                }

                AudioFormat format = new AudioFormat(sampleRate, 8, 1, true, false);
                Clip clip = AudioSystem.getClip();
                clip.open(new AudioInputStream(new ByteArrayInputStream(buffer), format, buffer.length));
                clip.start();
            } catch (Exception ignored) {}
        }).start();
    }

    // -------------------------------------------------------------
    // UPDATE LOGIC
    // -------------------------------------------------------------
    @Override
    public void actionPerformed(ActionEvent e) {
        animTick++;
        clockAngle += 0.8;

        // Blinking
        blinkTimer--;
        if (blinkTimer <= 0) {
            isBlinking = !isBlinking;
            blinkTimer = isBlinking ? 8 : (120 + rand.nextInt(140));
        }

        if (!gameWon) {
            totalTime += 0.016;
            if (isBlowing) {
                pressure += 0.42;

                // Air bubbles
                if (animTick % 2 == 0) {
                    airParticles.add(new AirParticle(350, 358, 480 + pressure * 0.8, 345, rand));
                }

                // Sweat drops
                if (pressure > 70.0 && rand.nextDouble() < 0.28) {
                    sweatParticles.add(new SweatDrop(280 + rand.nextInt(20) - 10, 305, rand));
                }

                shakeIntensity = pressure > 65.0 ? (pressure - 65.0) * 0.18 : 0.0;
            } else {
                pressure = Math.max(0.0, pressure - 0.20);
                shakeIntensity = Math.max(0.0, shakeIntensity - 0.25);
            }

            if (pressure >= 100.0) {
                pressure = 100.0;
                gameWon = true;
                burstTimer = 0;
                playTone("pop");
                playTone("win");
                for (int i = 0; i < 75; i++) {
                    plasticShreds.add(new PlasticShred(510, 330, rand));
                }
            }
        } else {
            burstTimer++;
            for (Confetti c : confettiList) c.update();
        }

        // Update particles
        airParticles.removeIf(p -> { p.update(); return p.life <= 0; });
        sweatParticles.removeIf(s -> { s.update(); return s.life <= 0; });
        plasticShreds.removeIf(sh -> { sh.update(); return sh.life <= 0; });

        repaint();
    }

    // -------------------------------------------------------------
    // RENDERING PIPELINE
    // -------------------------------------------------------------
    @Override
    protected void paintComponent(Graphics g) {
        super.paintComponent(g);
        Graphics2D g2 = (Graphics2D) g;
        g2.setRenderingHint(RenderingHints.KEY_ANTIALIASING, RenderingHints.VALUE_ANTIALIAS_ON);
        g2.setRenderingHint(RenderingHints.KEY_TEXT_ANTIALIASING, RenderingHints.VALUE_TEXT_ANTIALIAS_ON);

        drawClassroom(g2);
        drawDesk(g2);
        drawBoy(g2);
        drawBag(g2);

        // Draw Particles
        for (AirParticle p : airParticles) p.draw(g2);
        for (SweatDrop s : sweatParticles) s.draw(g2);
        for (PlasticShred sh : plasticShreds) sh.draw(g2);

        drawHud(g2);
        drawBurstAndVictory(g2);
    }

    private void drawClassroom(Graphics2D g2) {
        // Wainscot
        int wainscotY = 440;
        g2.setColor(COLOR_BG_WAINSCOT);
        g2.fillRect(0, wainscotY, SCREEN_WIDTH, SCREEN_HEIGHT - wainscotY);
        g2.setColor(COLOR_WOOD_DARK);
        g2.fillRect(0, wainscotY, SCREEN_WIDTH, 12);

        // Chalkboard
        int bx = 40, by = 45, bw = 520, bh = 220;
        g2.setColor(COLOR_WOOD_MID);
        g2.fillRoundRect(bx - 12, by - 12, bw + 24, bh + 24, 12, 12);
        g2.setColor(COLOR_WOOD_DARK);
        g2.drawRoundRect(bx - 12, by - 12, bw + 24, bh + 24, 12, 12);
        g2.setColor(COLOR_CHALKBOARD);
        g2.fillRoundRect(bx, by, bw, bh, 8, 8);

        // Chalk Text
        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 17));
        g2.setColor(new Color(255, 235, 130));
        g2.drawString("LESSON: AIR PRESSURE & PNEUMATICS", bx + 22, by + 30);
        g2.setColor(Color.WHITE);
        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 14));
        g2.drawString("MISSION: INFLATE BAG UNTIL IT BURSTS! 🎈💥", bx + 22, by + 65);
        g2.setColor(new Color(255, 175, 190));
        g2.drawString("P = Force / Area   |   Target = 100% POP!", bx + 22, by + 95);

        // Stick Figure Doodle
        int dx = bx + 410, dy = by + 130;
        g2.setColor(Color.WHITE);
        g2.drawOval(dx - 16, dy - 16, 32, 32);
        g2.drawLine(dx, dy + 16, dx, dy + 48);
        g2.drawLine(dx - 18, dy + 28, dx + 18, dy + 28);
        g2.drawLine(dx, dy + 48, dx - 14, dy + 72);
        g2.drawLine(dx, dy + 48, dx + 14, dy + 72);
        g2.setColor(new Color(255, 175, 190));
        g2.drawOval(dx + 26, dy - 2, 44, 44);
        g2.drawLine(dx + 18, dy + 28, dx + 28, dy + 22);

        // Clock
        int cx = 810, cy = 100, cr = 44;
        g2.setColor(new Color(240, 240, 245));
        g2.fillOval(cx - cr, cy - cr, cr * 2, cr * 2);
        g2.setColor(COLOR_WOOD_DARK);
        g2.setStroke(new BasicStroke(5));
        g2.drawOval(cx - cr, cy - cr, cr * 2, cr * 2);
        g2.setStroke(new BasicStroke(2));
        double sAng = Math.toRadians(clockAngle);
        g2.setColor(Color.RED);
        g2.drawLine(cx, cy, (int)(cx + Math.sin(sAng) * 34), (int)(cy - Math.cos(sAng) * 34));
    }

    private void drawDesk(Graphics2D g2) {
        int ty = 425;
        g2.setColor(COLOR_WOOD_LIGHT);
        g2.fillRoundRect(120, ty, 480, 36, 10, 10);
        g2.setColor(COLOR_WOOD_DARK);
        g2.setStroke(new BasicStroke(3));
        g2.drawRoundRect(120, ty, 480, 36, 10, 10);

        // Legs
        g2.setColor(new Color(65, 75, 85));
        g2.fillRect(160, ty + 36, 16, SCREEN_HEIGHT - (ty + 36));
        g2.fillRect(540, ty + 36, 16, SCREEN_HEIGHT - (ty + 36));
        g2.setColor(COLOR_WOOD_MID);
        g2.fillRect(176, ty + 36, 364, 90);

        // Pencil Cup & Books
        g2.setColor(new Color(220, 50, 50));
        g2.fillRoundRect(145, ty - 12, 60, 12, 4, 4);
        g2.setColor(new Color(50, 140, 220));
        g2.fillRoundRect(148, ty - 23, 54, 11, 4, 4);
    }

    private void drawBoy(Graphics2D g2) {
        double bx = 270;
        double by = 310;
        if (shakeIntensity > 0) {
            bx += (rand.nextDouble() * 2 - 1) * shakeIntensity;
            by += (rand.nextDouble() * 2 - 1) * shakeIntensity;
        }

        // Torso
        g2.setColor(COLOR_SHIRT);
        g2.fillRoundRect((int)bx - 42, (int)by + 50, 84, 85, 20, 20);
        // Collar & Tie
        g2.setColor(Color.WHITE);
        g2.fillPolygon(new int[]{(int)bx - 26, (int)bx, (int)bx + 26}, new int[]{(int)by + 50, (int)by + 70, (int)by + 50}, 3);
        g2.setColor(COLOR_TIE);
        g2.fillPolygon(new int[]{(int)bx - 7, (int)bx + 7, (int)bx + 10, (int)bx, (int)bx - 10},
                new int[]{(int)by + 68, (int)by + 68, (int)by + 115, (int)by + 126, (int)by + 115}, 5);

        // Arms
        if (gameWon) {
            g2.setStroke(new BasicStroke(16, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
            g2.setColor(COLOR_SHIRT);
            g2.drawLine((int)bx - 36, (int)by + 65, (int)bx - 65, (int)by + 10);
            g2.drawLine((int)bx + 36, (int)by + 65, (int)bx + 65, (int)by + 10);
            g2.setColor(COLOR_SKIN);
            g2.fillOval((int)bx - 77, (int)by - 2, 24, 24);
            g2.fillOval((int)bx + 53, (int)by - 2, 24, 24);
        } else {
            g2.setStroke(new BasicStroke(15, BasicStroke.CAP_ROUND, BasicStroke.JOIN_ROUND));
            g2.setColor(COLOR_SHIRT);
            g2.drawLine((int)bx - 36, (int)by + 68, (int)bx + 30, (int)by + 78);
            g2.drawLine((int)bx + 20, (int)by + 72, (int)bx + 68, (int)by + 65);
            g2.setColor(COLOR_SKIN);
            g2.fillOval((int)bx + 42, (int)by + 54, 20, 20);
        }

        // Head
        int hx = (int)bx, hy = (int)by, hr = 42;
        Color skin = COLOR_SKIN;
        if (isBlowing) {
            float strain = (float) Math.min(1.0, pressure / 100.0);
            skin = new Color(255, (int)(213 - 93 * strain), (int)(179 - 79 * strain));
        }
        g2.setColor(skin);
        g2.fillOval(hx - hr, hy - hr, hr * 2, hr * 2);
        g2.setColor(new Color(180, 120, 80));
        g2.setStroke(new BasicStroke(3));
        g2.drawOval(hx - hr, hy - hr, hr * 2, hr * 2);

        // Cheeks
        if (isBlowing && !gameWon) {
            int puff = 14 + (int)(pressure / 100.0 * 10);
            g2.setColor(COLOR_CHEEKS_BLOW);
            g2.fillOval(hx - 24 - puff, hy + 14 - puff, puff * 2, puff * 2);
            g2.fillOval(hx + 26 - puff, hy + 14 - puff, puff * 2 + 4, puff * 2 + 4);
        } else {
            g2.setColor(new Color(255, 170, 160));
            g2.fillOval(hx - 30, hy + 6, 16, 16);
            g2.fillOval(hx + 14, hy + 6, 16, 16);
        }

        // Eyes
        int eyeY = hy - 4;
        if (gameWon) {
            g2.setColor(new Color(30, 30, 30));
            g2.drawArc(hx - 24, eyeY - 6, 18, 16, 0, 180);
            g2.drawArc(hx + 8, eyeY - 6, 18, 16, 0, 180);
        } else if (isBlowing) {
            g2.setColor(new Color(30, 30, 30));
            g2.drawLine(hx - 22, eyeY - 3, hx - 10, eyeY + 3);
            g2.drawLine(hx - 22, eyeY + 3, hx - 10, eyeY - 3);
            g2.drawLine(hx + 8, eyeY - 3, hx + 20, eyeY + 3);
            g2.drawLine(hx + 8, eyeY + 3, hx + 20, eyeY - 3);
        } else {
            g2.setColor(Color.WHITE);
            g2.fillOval(hx - 22, eyeY - 9, 18, 18);
            g2.fillOval(hx + 4, eyeY - 9, 18, 18);
            g2.setColor(new Color(40, 80, 180));
            g2.fillOval(hx - 18, eyeY - 6, 12, 12);
            g2.fillOval(hx + 8, eyeY - 6, 12, 12);
        }

        // Mouth
        int my = hy + 22;
        if (gameWon) {
            g2.setColor(new Color(180, 20, 20));
            g2.fillArc(hx - 18, my - 6, 36, 24, 180, 180);
            g2.setColor(Color.WHITE);
            g2.fillRect(hx - 12, my, 24, 6);
        } else if (isBlowing) {
            g2.setColor(new Color(220, 70, 70));
            g2.fillOval(hx + 28, my - 8, 18, 14);
        } else {
            g2.setColor(new Color(80, 40, 30));
            g2.drawArc(hx - 10, my - 6, 20, 14, 200, 140);
        }

        // Hair
        g2.setColor(COLOR_HAIR);
        g2.fillPolygon(new int[]{hx - 44, hx - 46, hx - 30, hx - 18, hx + 4, hx + 36, hx + 46, hx + 10},
                new int[]{hy - 10, hy - 35, hy - 48, hy - 56, hy - 58, hy - 44, hy - 20, hy - 24}, 8);
    }

    private void drawBag(Graphics2D g2) {
        if (gameWon) return;

        double progress = pressure / 100.0;
        int rx = (int)(32 + progress * 135);
        int ry = (int)(28 + progress * 115);

        double wAmp = progress * (pressure < 70 ? 6.0 : 14.0);
        double wx = Math.sin(animTick * 0.4) * wAmp;
        double wy = Math.cos(animTick * 0.5) * wAmp;

        int cx = (int)(328 + rx * 0.95 + wx);
        int cy = (int)(330 - ry * 0.15 + wy);

        // Translucent Bag Body
        Composite oldComp = g2.getComposite();
        float alpha = (float) Math.max(0.2, 0.72 - progress * 0.22);
        g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, alpha));
        g2.setColor(COLOR_BAG_TINT);
        g2.fillOval(cx - rx, cy - ry, rx * 2, ry * 2);

        // Highlight shine
        g2.setComposite(AlphaComposite.getInstance(AlphaComposite.SRC_OVER, 0.85f));
        g2.setColor(Color.WHITE);
        g2.setStroke(new BasicStroke(4));
        g2.drawArc((int)(cx - rx * 0.8), (int)(cy - ry * 0.78), (int)(rx * 0.9), (int)(ry * 0.55), 70, 90);

        // Border
        g2.setComposite(oldComp);
        g2.setColor(new Color(50, 160, 220));
        g2.setStroke(new BasicStroke(3));
        g2.drawOval(cx - rx, cy - ry, rx * 2, ry * 2);
    }

    private void drawHud(Graphics2D g2) {
        int bw = 380, bh = 32;
        int bx = (SCREEN_WIDTH - bw) / 2, by = 18;

        g2.setColor(new Color(240, 240, 245));
        g2.fillRoundRect(bx - 6, by - 6, bw + 12, bh + 12, 16, 16);
        g2.setColor(COLOR_WOOD_DARK);
        g2.setStroke(new BasicStroke(3));
        g2.drawRoundRect(bx - 6, by - 6, bw + 12, bh + 12, 16, 16);
        g2.setColor(new Color(210, 215, 225));
        g2.fillRoundRect(bx, by, bw, bh, 10, 10);

        // Gradient color
        Color fillCol = pressure < 50 ? new Color(46, 204, 113) :
                (pressure < 78 ? new Color(241, 196, 15) : new Color(231, 76, 60));
        int fw = (int)(pressure / 100.0 * bw);
        if (fw > 0) {
            g2.setColor(fillCol);
            g2.fillRoundRect(bx, by, fw, bh, 10, 10);
        }

        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 18));
        g2.setColor(Color.BLACK);
        String pText = "PRESSURE: " + (int)pressure + "%";
        FontMetrics fm = g2.getFontMetrics();
        g2.drawString(pText, bx + (bw - fm.stringWidth(pText)) / 2, by + 22);

        // Spacebar Prompt
        if (!gameWon) {
            int px = SCREEN_WIDTH / 2 - 210, py = SCREEN_HEIGHT - 65;
            g2.setColor(Color.WHITE);
            g2.fillRoundRect(px, py, 420, 44, 24, 24);
            g2.setColor(COLOR_SHIRT);
            g2.setStroke(new BasicStroke(3));
            g2.drawRoundRect(px, py, 420, 44, 24, 24);

            String prompt = isBlowing ? "💨 BLOWING HARD!! KEEP HOLDING!" : "💨 HOLD [SPACEBAR] TO BLOW!";
            g2.drawString(prompt, px + (420 - fm.stringWidth(prompt)) / 2, py + 28);
        }
    }

    private void drawBurstAndVictory(Graphics2D g2) {
        if (!gameWon) return;

        if (burstTimer < 35) {
            // POP starburst
            g2.setFont(new Font("Impact", Font.BOLD, 74));
            g2.setColor(Color.RED);
            g2.drawString("POP!!", 460, 360);
        }

        // Confetti
        for (Confetti c : confettiList) c.draw(g2);

        // Victory Banner
        int mw = 520, mh = 320;
        int mx = (SCREEN_WIDTH - mw) / 2, my = (SCREEN_HEIGHT - mh) / 2 - 20;

        g2.setColor(Color.WHITE);
        g2.fillRoundRect(mx, my, mw, mh, 20, 20);
        g2.setColor(new Color(255, 215, 0));
        g2.setStroke(new BasicStroke(5));
        g2.drawRoundRect(mx, my, mw, mh, 20, 20);

        g2.setColor(new Color(255, 80, 50));
        g2.fillRoundRect(mx + 30, my - 24, mw - 60, 56, 14, 14);
        g2.setColor(Color.WHITE);
        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 32));
        g2.drawString("🎉 YOU WIN! 🎉", mx + 130, my + 16);

        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 22));
        g2.setColor(new Color(46, 125, 50));
        g2.drawString("BAG BURSTED SUCCESSFULLY!", mx + 85, my + 75);

        g2.setFont(new Font("Comic Sans MS", Font.BOLD, 17));
        g2.setColor(COLOR_SHIRT);
        g2.drawString(String.format("⏱️ Burst Time: %.1fs   |   💥 Pressure: 100%%", totalTime), mx + 100, my + 130);

        // Button
        g2.setColor(btnHover ? new Color(39, 174, 96) : new Color(46, 204, 113));
        g2.fillRoundRect(btnRestartRect.x, btnRestartRect.y, btnRestartRect.width, btnRestartRect.height, 16, 16);
        g2.setColor(Color.WHITE);
        g2.drawString("PLAY AGAIN (Press R)", btnRestartRect.x + 22, btnRestartRect.y + 32);
    }

    // -------------------------------------------------------------
    // INPUT HANDLERS
    // -------------------------------------------------------------
    @Override
    public void keyPressed(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.VK_SPACE && !gameWon) {
            if (!isBlowing) playTone("blow");
            isBlowing = true;
        } else if (e.getKeyCode() == KeyEvent.VK_R) {
            resetGame();
        } else if (e.getKeyCode() == KeyEvent.VK_M) {
            soundMuted = !soundMuted;
        }
    }

    @Override
    public void keyReleased(KeyEvent e) {
        if (e.getKeyCode() == KeyEvent.VK_SPACE) isBlowing = false;
    }

    @Override
    public void mouseClicked(MouseEvent e) {
        if (gameWon && btnRestartRect.contains(e.getPoint())) resetGame();
    }

    @Override public void keyTyped(KeyEvent e) {}
    @Override public void mousePressed(MouseEvent e) {}
    @Override public void mouseReleased(MouseEvent e) {}
    @Override public void mouseEntered(MouseEvent e) {}
    @Override public void mouseExited(MouseEvent e) {}

    // -------------------------------------------------------------
    // INNER CLASSES: PARTICLES
    // -------------------------------------------------------------
    static class AirParticle {
        double x, y, vx, vy, radius;
        int life = 24;
        AirParticle(double sx, double sy, double tx, double ty, Random r) {
            x = sx; y = sy;
            double ang = Math.atan2(ty - sy, tx - sx) + (r.nextDouble() * 0.6 - 0.3);
            double spd = 4.0 + r.nextDouble() * 4.0;
            vx = Math.cos(ang) * spd;
            vy = Math.sin(ang) * spd;
            radius = 3.0 + r.nextDouble() * 3.0;
        }
        void update() { x += vx; y += vy; vx *= 0.94; vy *= 0.94; life--; }
        void draw(Graphics2D g2) {
            g2.setColor(new Color(255, 255, 255, Math.max(0, life * 9)));
            g2.fillOval((int)(x - radius), (int)(y - radius), (int)(radius * 2), (int)(radius * 2));
        }
    }

    static class SweatDrop {
        double x, y, vx, vy;
        int life = 25;
        SweatDrop(double sx, double sy, Random r) {
            x = sx; y = sy;
            vx = 2.0 + r.nextDouble() * 2.5;
            vy = -3.5 + r.nextDouble() * 2.0;
        }
        void update() { x += vx; y += vy; vy += 0.3; life--; }
        void draw(Graphics2D g2) {
            if (life > 0) {
                g2.setColor(COLOR_SWEAT);
                g2.fillOval((int)x, (int)y, 7, 7);
            }
        }
    }

    static class PlasticShred {
        double x, y, vx, vy, size;
        int life = 60;
        PlasticShred(double ox, double oy, Random r) {
            x = ox; y = oy;
            double ang = r.nextDouble() * 2 * Math.PI;
            double spd = 6.0 + r.nextDouble() * 10.0;
            vx = Math.cos(ang) * spd;
            vy = Math.sin(ang) * spd - 3.0;
            size = 10.0 + r.nextDouble() * 14.0;
        }
        void update() { x += vx; y += vy; vy += 0.35; vx *= 0.97; life--; }
        void draw(Graphics2D g2) {
            if (life > 0) {
                g2.setColor(new Color(100, 210, 255, Math.max(0, life * 4)));
                g2.fillOval((int)x, (int)y, (int)size, (int)(size * 0.7));
            }
        }
    }

    static class Confetti {
        double x, y, vx, vy;
        Color color;
        Random rand;
        Confetti(Random r) {
            rand = r;
            x = r.nextDouble() * SCREEN_WIDTH;
            y = r.nextDouble() * -300;
            vx = r.nextDouble() * 2 - 1;
            vy = 3.0 + r.nextDouble() * 3.0;
            Color[] cols = {Color.RED, Color.ORANGE, Color.YELLOW, Color.GREEN, Color.CYAN, Color.MAGENTA};
            color = cols[r.nextInt(cols.length)];
        }
        void update() {
            y += vy;
            x += vx + Math.sin(y * 0.05);
            if (y > SCREEN_HEIGHT) { y = -20; x = rand.nextDouble() * SCREEN_WIDTH; }
        }
        void draw(Graphics2D g2) {
            g2.setColor(color);
            g2.fillRect((int)x, (int)y, 9, 6);
        }
    }

    // -------------------------------------------------------------
    // MAIN ENTRY POINT
    // -------------------------------------------------------------
    public static void main(String[] args) {
        SwingUtilities.invokeLater(() -> {
            JFrame frame = new JFrame("The Great Bag Buster! (Polythene Bag Pop Game)");
            frame.setDefaultCloseOperation(JFrame.EXIT_ON_CLOSE);
            frame.setContentPane(new BagBusterGame());
            frame.pack();
            frame.setLocationRelativeTo(null);
            frame.setResizable(false);
            frame.setVisible(true);
        });
    }
}

