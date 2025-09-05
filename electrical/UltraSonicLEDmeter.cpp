// -------------------------------------------------
// DistanceMeter Class
// Author: Rafael A Castro
// Date: 9/2/2025
// Website: www.castron.org/cpp
// -------------------------------------------------

class DistanceMeter
{
private:
    int trigPin;
    int echoPin;
    int *ledPins;
    int numLEDs;
    float maxDistanceCm;

public:
    DistanceMeter(int tPin, int ePin, int *leds, int nLEDs, float maxDistCm)
    {
        trigPin = tPin;
        echoPin = ePin;
        ledPins = leds;
        numLEDs = nLEDs;
        maxDistanceCm = maxDistCm;

        pinMode(trigPin, OUTPUT);
        pinMode(echoPin, INPUT);
        for (int i = 0; i < numLEDs; i++)
        {
            pinMode(ledPins[i], OUTPUT);
            analogWrite(ledPins[i], 0); // LEDs start OFF
        }
    }

    // Read distance in cm
    float readCm()
    {
        digitalWrite(trigPin, LOW);
        delayMicroseconds(2);
        digitalWrite(trigPin, HIGH);
        delayMicroseconds(10);
        digitalWrite(trigPin, LOW);

        long duration = pulseIn(echoPin, HIGH, 25000); // 25ms timeout
        float distance = duration * 0.034 / 2;
        if (distance == 0 || distance > maxDistanceCm)
            distance = maxDistanceCm; // clamp
        return distance;
    }

    // Update LEDs smoothly, right (D2) → left (D8)
    void updateLEDs()
    {
        float distance = readCm();
        distance = constrain(distance, 0, maxDistanceCm);

        float ledValue = (1.0 - distance / maxDistanceCm) * numLEDs;
        ledValue = constrain(ledValue, 0, numLEDs);

        for (int i = 0; i < numLEDs; i++)
        {
            int ledIndex = i; // D2 → D8
            if (i < floor(ledValue))
            {
                analogWrite(ledPins[ledIndex], 255);
            }
            else if (i == floor(ledValue))
            {
                int pwm = (ledValue - floor(ledValue)) * 255;
                analogWrite(ledPins[ledIndex], pwm);
            }
            else
            {
                analogWrite(ledPins[ledIndex], 0);
            }
        }
    }

    void setMaxDistance(float maxDistCm)
    {
        maxDistanceCm = maxDistCm;
    }
};

// ------------------------
// Main Sketch
// ------------------------
int ledPins[] = {2, 3, 4, 5, 6, 7, 8};      // Rightmost D2 → Leftmost D8
DistanceMeter meter(9, 10, ledPins, 7, 25); // Max distance ~25cm for demo

void setup()
{
    Serial.begin(9600);
    for (int i = 0; i < 7; i++)
    {
        analogWrite(ledPins[i], 0); // Ensure all LEDs start OFF
    }
}

void loop()
{
    meter.updateLEDs();
    float distance = meter.readCm();
    Serial.print("Distance: ");
    Serial.print(distance);
    Serial.println(" cm");
    delay(10); // smooth update
}
