import java.util.*;
import java.util.List;
import java.util.ArrayList;
import java.util.Arrays;
import java.lang.Math;
import java.lang.Integer;

public class LongDigit_Pi {
    static int max = 1000;
    public static void main(String[] args) throws Exception {
        int digit = 100;
        int updateNum = 30;
        int sqrtQuality = 100;

        if (args.length >= 1) digit = Integer.parseInt(args[0]);
        if (args.length >= 2) updateNum = Integer.parseInt(args[1]); 
        if (args.length >= 3) sqrtQuality = Integer.parseInt(args[2]);

        int[] a = cast(1.0);
        int[] b = div(cast(1.0), sqrt(cast(2), sqrtQuality, digit), digit);
        int[] t = cast(0.25);
        int[] p = cast(1.0);
        int[] piTemp = new int[0];
        for (int i = 0; i < updateNum; i++) {
            int[] _a = div(add(a, b), cast(2.0), digit);
            int[] _b = sqrt(multi(a, b), sqrtQuality, digit);
            int[] _t = sub(t, multi(p, multi(sub(a, _a), sub(a, _a))));
            int[] _p = multi(cast(2), p);
            if (Arrays.equals(a, _a) && Arrays.equals(b, _b) && Arrays.equals(t, _t) && Arrays.equals(p, _p)) break;
            a = normalize(_a);
            b = normalize(_b);
            t = normalize(_t);
            p = normalize(_p);
            int[] pi = div(multi(add(a, b), add(a, b)), multi(cast(4), t), digit);
            System.out.print(i + ". 円周率: ");
            print(pi);
            if (Arrays.equals(pi, piTemp)) {
                System.out.print("result: ");
                print(pi);
                break;
            }
            piTemp = new int[pi.length];
            for (int k = 0; k < pi.length; k++) piTemp[k] = pi[k];

        }
    }

    public static int getElementDigit() {
        return Integer.toString(max).length() - 1;
    }
    
    private static int[] cast(double num) { //誤差が大きい
        List<Integer> a = new ArrayList<Integer>();
        a.add(Integer.valueOf((int)num));
        double _num = num;
        while (_num > 0) {
            _num = (_num * max) % max;
            a.add(Integer.valueOf((int)_num));
        }
        return a.stream().mapToInt(i->i).toArray();
    }
    
    private static int[] add(int[] a, int[] b) {
        int size = a.length >= b.length ? a.length : b.length;
        int[] c = new int[size];
        for (int i = 0; i < size; i++) {
            int index = (size - 1) - i;
            int temp = c[index];
            if (a.length > index) temp += a[index];
            if (b.length > index) temp += b[index];
            if (index > 0) { //最上位は繰り上がりなし
                c[index - 1] += (temp / max);
                c[index] = (temp % max);
            } else c[index] = temp;
        }
        return c;
    }
    
    private static int[] sub(int[] a, int[] b) {
        int size = a.length >= b.length ? a.length : b.length;
        int[] c = new int[size];
        boolean greaterThanA = !greater(a, b);
        if (greaterThanA) {
            int[] tempArray = a;
            a = b;
            b = tempArray;
        }
        for (int i = 0; i < size; i++) {
            int index = (size - 1) - i;
            int temp = c[index];
            if (a.length > index) temp += a[index];
            if (b.length > index) temp -= b[index];
            if (temp < 0) {
                if (index > 0) {
                    c[index - 1] -= ((temp / max) + 1);
                    temp += ((temp / max) + 1) * max;
                }
            }
            c[index] = temp;
        }
        if (greaterThanA) {
            for (int i = 0; i < c.length; i++) {
                if (c[i] > 0) {
                    c[i] *= -1;
                    break;
                }
            }
        }
        return c;
    }
    private static boolean greater(int[] a, int[] b) {
        int size = a.length > b.length ? a.length : b.length;
        for (int i = 0; i < size; i++) {
            if (a.length < i + 1 || b.length < i + 1) return false;
            if (a[i] - b[i] > 0) return true;
            else if (a[i] - b[i] < 0) return false;
        }
        return false;
    }
    
    private static int[] multi(int[] a, int[] b) {
        int aSign = sign(a);
        int bSign = sign(b);
        int[] _a = abs(a);
        int[] _b = abs(b);
        int size = (a.length - 1) + (b.length - 1) + 1;
        int[] c = new int[size];
        for (int i = 0; i < _a.length; i++) {
            for (int k = 0; k < _b.length; k++) {
                c[i + k] += _a[i] * _b[k];
            }
        }
        for (int i = 0; i < size; i++) {
            int index = (size - 1) - i;
            int temp = c[index];
            if (index > 0) { //最上位は繰り上がりなし
                c[index - 1] += (temp / max);
                c[index] = (temp % max);
            } else c[index] = temp;
        }
        for (int i = 0; i < size; i++) {
            if (c[i] > 0) {
                c[i] *= aSign * bSign;
                break;
            }
        }
        return c;
    }
    
    private static int[] div(int[] a, int[] b, int digit) {
        int aSign = sign(a);
        int bSign = sign(b);
        int[] _a = abs(a);
        int[] _b = abs(b);
        int[] div = new int[]{0};
        int shift = 0;
        int[] remain = new int[_a.length];
        for (int i = 0; i < _a.length; i++) remain[i] = _a[i];
        while (true) {
            int[] temp = sub(remain, shiftRight(_b, shift));
            //print(div);
            //print(remain);
            if (sign(temp) >= 0) {
                remain = temp;
                div = add(div, shiftRight(cast(1), shift));
            } else shift++;
            if (shift >= digit) break;
            if (zero(remain)) break;
        }
        for (int i = 0; i < div.length; i++) {
            if (div[i] > 0) {
                div[i] *= aSign * bSign;
                break;
            }
        }
        return div;
    }

    public static int sign(int[] a) {
        for (int n : a) {
            if (n > 0) return 1;
            else if (n < 0) return -1;
        }
        return 0;
    }

    public static int[] abs(int[] a) {
        int[] b = new int[a.length];
        for (int i = 0; i < a.length; i++) 
            if (a[i] < 0) b[i] = a[i] * -1;
            else b[i] = a[i];
        return b;
    }

    public static boolean zero(int[] a) {
        for (int n : a) if (n != 0) return false;
        return true;
    }

    public static int[] shiftRight(int[] a, int shift) {
        if (shift <= 0) return a;
        int add = (int)(shift / getElementDigit()) + 1;
        int[] b = new int[a.length];
        for (int i = 0; i < a.length; i++) b[i] = a[i];
        int[] c = new int[a.length + add];
        for (int i = 0; i < b.length; i++) {
            int index = (b.length - 1) - i;
            int temp = b[index];
            for (int k = 0; k < getElementDigit(); k++) {
                int indexK = (getElementDigit() - 1) - k;
                temp %= pow(10, indexK + 1);
                int num = temp / pow(10, indexK);
                c[index + (shift + (getElementDigit() - 1) - indexK) / getElementDigit()] += num * pow(10, ((shift + indexK + 1 + ((shift - 1) % getElementDigit())) % getElementDigit()));
            }
        }
        return c;
    }
    public static int pow(int a, int b) {
        int c = 1;
        for (int i = 0; i < b; i++) c *= a;
        return c;
    }

    public static int[] sqrt(int[] a, int count, int digit) {
        int[] b = new int[count * (a.length - 1) + 1];
        for (int i = 0; i < a.length; i++) b[i] = a[i];
        for (int i = 0; i < count; i++) {
            b = div(add(multi(b, b), a), multi(cast(2), b), digit);
        }
        return b;
    }

    public static int[] normalize(int[] a) {
        int zeroElement = 0;
        for (int i = 0; i < a.length; i++) {
            int index = (a.length - 1) - i;
            if (a[index] == 0) zeroElement++;
            else break;
        }
        int[] b = new int[a.length - zeroElement];
        for (int i = 0; i < b.length; i++) b[i] = a[i];
        return b;
    }

    public static void print(int[] a) {
        for (int i = 0; i < a.length; i++) {
                int len = Integer.toString(max).length() - 1;
                String num = Integer.toString(a[i]);
                while (num.length() < len) {
                    num = "0" + num;
                }
                System.out.print(num + " ");
        }
        System.out.println();
    }
    public static void printDigit(int[] a) {
        System.out.println("digit: " + a.length * getElementDigit());
    }
}
