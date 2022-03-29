public static class KuritaroMath {
  public static float Mod(float left, float right) {
    float add = Math.Max(0f, right * (int)(-left / right + 1));
    return (left + add) % right;
  }
}
